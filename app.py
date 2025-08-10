import os
import logging
import csv
import io
from flask import Flask, jsonify, render_template, request, Response, make_response
from werkzeug.middleware.proxy_fix import ProxyFix
from models import db, ExchangeRate, UpdateLog, ExchangeRateHistory, ApiMetrics
from database_service import DatabaseService
from datetime import datetime, timedelta
import time
from functools import wraps
from sqlalchemy import func, desc
from config import get_config, DatabaseConfig

# Obtener configuración del entorno
config = get_config()

# Configure logging
logging.basicConfig(level=getattr(logging, config.LOG_LEVEL))
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.secret_key = config.SECRET_KEY
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure database using the new configuration system
db_config = DatabaseConfig.get_database_config()
app.config.update(db_config)

# Initialize database
db.init_app(app)

# Simple rate limiting
last_request_time = {}
RATE_LIMIT_SECONDS = config.RATE_LIMIT_SECONDS  # Get from configuration

# Initialize database tables and service within app context
with app.app_context():
    db.create_all()
    db_service = DatabaseService()

def rate_limit(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR', 'unknown'))
        current_time = time.time()
        
        if client_ip in last_request_time:
            time_since_last = current_time - last_request_time[client_ip]
            if time_since_last < RATE_LIMIT_SECONDS:
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'message': f'Please wait {RATE_LIMIT_SECONDS - int(time_since_last)} seconds before making another request',
                    'retry_after': RATE_LIMIT_SECONDS - int(time_since_last)
                }), 429
        
        last_request_time[client_ip] = current_time
        return f(*args, **kwargs)
    return decorated_function

def track_metrics(f):
    """Decorator to track API usage metrics"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        client_ip = request.environ.get('REMOTE_ADDR', request.remote_addr)
        response_format = get_response_format()
        
        try:
            response = f(*args, **kwargs)
            # Extract status code from response
            if isinstance(response, tuple):
                status_code = response[1] if len(response) > 1 else 200
            else:
                status_code = 200
                
        except Exception as e:
            status_code = 500
            response = f(*args, **kwargs)  # Let the original function handle the error
            
        end_time = time.time()
        response_time_ms = (end_time - start_time) * 1000
        
        # Save metrics to database (async to avoid blocking)
        try:
            metric = ApiMetrics(
                endpoint=request.endpoint,
                method=request.method,
                ip_address=client_ip,
                response_format=response_format,
                status_code=status_code,
                response_time_ms=response_time_ms
            )
            db.session.add(metric)
            db.session.commit()
        except Exception as e:
            logger.warning(f"Failed to save metrics: {str(e)}")
            
        return response
    return decorated_function

def get_response_format():
    """Determine response format from request parameters or headers"""
    # Check query parameter first
    format_param = request.args.get('format', '').lower()
    if format_param in ['json', 'csv', 'xml']:
        return format_param
    
    # Check Accept header
    accept_header = request.headers.get('Accept', '')
    if 'text/csv' in accept_header:
        return 'csv'
    elif 'application/xml' in accept_header or 'text/xml' in accept_header:
        return 'xml'
    
    # Default to JSON
    return 'json'

def format_response(data, format_type='json', endpoint_type='single'):
    """Format response data in requested format"""
    timestamp = datetime.now().isoformat()
    
    if format_type == 'csv':
        return format_csv_response(data, endpoint_type)
    elif format_type == 'xml':
        return format_xml_response(data, endpoint_type, timestamp)
    else:
        return jsonify(data)

def format_csv_response(data, endpoint_type):
    """Format response as CSV"""
    output = io.StringIO()
    
    if endpoint_type == 'all_rates' and data.get('success') and 'data' in data:
        # CSV for all rates
        writer = csv.writer(output)
        writer.writerow(['Currency', 'Rate', 'Date_Published', 'Last_Updated', 'Base_Currency'])
        
        rates = data['data']['rates']
        date_published = data['data'].get('date', '')
        last_updated = data['data'].get('last_updated', '')
        base_currency = data['data'].get('base_currency', 'VES')
        
        for currency, rate in rates.items():
            writer.writerow([currency, rate, date_published, last_updated, base_currency])
    
    elif endpoint_type == 'single_rate' and data.get('success'):
        # CSV for single rate
        writer = csv.writer(output)
        writer.writerow(['Currency', 'Rate', 'Date_Published', 'Last_Updated', 'Timestamp'])
        writer.writerow([
            data.get('currency', ''),
            data.get('rate', ''),
            data.get('date_published', ''),
            data.get('last_updated', ''),
            data.get('timestamp', '')
        ])
    
    elif endpoint_type == 'status' and data.get('success'):
        # CSV for status
        writer = csv.writer(output)
        writer.writerow(['Metric', 'Value'])
        writer.writerow(['System_Status', data.get('system_status', '')])
        writer.writerow(['Rates_Available', data.get('rates_available', '')])
        writer.writerow(['Last_Update', data.get('last_update', '')])
        writer.writerow(['Timestamp', data.get('timestamp', '')])
    
    else:
        # Error response in CSV
        writer = csv.writer(output)
        writer.writerow(['Error', 'Message', 'Timestamp'])
        writer.writerow([
            data.get('error', 'Unknown error'),
            data.get('message', ''),
            data.get('timestamp', timestamp)
        ])
    
    csv_content = output.getvalue()
    output.close()
    
    response = make_response(csv_content)
    response.headers['Content-Type'] = 'text/csv; charset=utf-8'
    response.headers['Content-Disposition'] = 'attachment; filename=bcv_rates.csv'
    return response

def format_xml_response(data, endpoint_type, timestamp):
    """Format response as XML"""
    if endpoint_type == 'all_rates' and data.get('success') and 'data' in data:
        # XML for all rates
        rates = data['data']['rates']
        date_published = data['data'].get('date', '')
        last_updated = data['data'].get('last_updated', '')
        base_currency = data['data'].get('base_currency', 'VES')
        
        xml_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<bcv_rates>
    <success>true</success>
    <timestamp>{timestamp}</timestamp>
    <source>{data.get('source', '')}</source>
    <data>
        <base_currency>{base_currency}</base_currency>
        <date>{date_published}</date>
        <last_updated>{last_updated}</last_updated>
        <rates>'''
        
        for currency, rate in rates.items():
            xml_content += f'''
            <rate>
                <currency>{currency}</currency>
                <value>{rate}</value>
            </rate>'''
        
        xml_content += '''
        </rates>
    </data>
</bcv_rates>'''
    
    elif endpoint_type == 'single_rate' and data.get('success'):
        # XML for single rate
        xml_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<bcv_rate>
    <success>true</success>
    <currency>{data.get('currency', '')}</currency>
    <rate>{data.get('rate', '')}</rate>
    <date_published>{data.get('date_published', '')}</date_published>
    <last_updated>{data.get('last_updated', '')}</last_updated>
    <timestamp>{timestamp}</timestamp>
    <source>{data.get('source', '')}</source>
</bcv_rate>'''
    
    elif endpoint_type == 'status' and data.get('success'):
        # XML for status
        xml_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<bcv_status>
    <success>true</success>
    <system_status>{data.get('system_status', '')}</system_status>
    <rates_available>{data.get('rates_available', '')}</rates_available>
    <last_update>{data.get('last_update', '')}</last_update>
    <timestamp>{timestamp}</timestamp>
</bcv_status>'''
    
    else:
        # Error response in XML
        xml_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<bcv_error>
    <success>false</success>
    <error>{data.get('error', 'Unknown error')}</error>
    <message>{data.get('message', '')}</message>
    <timestamp>{timestamp}</timestamp>
</bcv_error>'''
    
    response = make_response(xml_content)
    response.headers['Content-Type'] = 'application/xml; charset=utf-8'
    return response

@app.route('/')
def index():
    """Main page with API documentation and test interface"""
    return render_template('index.html')

@app.route('/api/rates', methods=['GET'])
@rate_limit
@track_metrics
def get_all_rates():
    """Get all available currency exchange rates from database"""
    try:
        logger.info("Fetching all currency rates from database")
        rates_data = db_service.get_rates_with_auto_update()
        
        response_format = get_response_format()
        
        if not rates_data:
            error_response = {
                'error': 'No data available',
                'message': 'Unable to fetch exchange rates from database',
                'timestamp': datetime.now().isoformat()
            }
            if response_format == 'json':
                return jsonify(error_response), 503
            else:
                return format_response(error_response, response_format, 'all_rates')
        
        response_data = {
            'success': True,
            'data': rates_data,
            'timestamp': datetime.now().isoformat(),
            'source': 'Banco Central de Venezuela (BCV) - Cached'
        }
        
        logger.info(f"Successfully fetched rates from database: {len(rates_data.get('rates', {}))}")
        
        if response_format == 'json':
            return jsonify(response_data)
        else:
            return format_response(response_data, response_format, 'all_rates')
        
    except Exception as e:
        logger.error(f"Error fetching all rates: {str(e)}")
        error_response = {
            'error': 'Internal server error',
            'message': 'An error occurred while fetching exchange rates',
            'timestamp': datetime.now().isoformat()
        }
        
        response_format = get_response_format()
        if response_format == 'json':
            return jsonify(error_response), 500
        else:
            return format_response(error_response, response_format, 'all_rates')

@app.route('/api/rates/usd', methods=['GET'])
@rate_limit
def get_usd_rate():
    """Get USD exchange rate from database"""
    try:
        logger.info("Fetching USD rate from database")
        rate_data = db_service.get_currency_rate('USD')
        
        response_format = get_response_format()
        
        if not rate_data:
            error_response = {
                'error': 'Currency not found',
                'message': 'USD exchange rate not available',
                'timestamp': datetime.now().isoformat()
            }
            if response_format == 'json':
                return jsonify(error_response), 404
            else:
                return format_response(error_response, response_format, 'single_rate')
        
        response_data = {
            'success': True,
            'currency': 'USD',
            'rate': rate_data['rate'],
            'date_published': rate_data.get('date_published'),
            'last_updated': rate_data.get('updated_at'),
            'timestamp': datetime.now().isoformat(),
            'source': 'Banco Central de Venezuela (BCV) - Cached'
        }
        
        logger.info(f"Successfully fetched USD rate: {rate_data['rate']}")
        
        if response_format == 'json':
            return jsonify(response_data)
        else:
            return format_response(response_data, response_format, 'single_rate')
        
    except Exception as e:
        logger.error(f"Error fetching USD rate: {str(e)}")
        error_response = {
            'error': 'Internal server error',
            'message': 'An error occurred while fetching USD exchange rate',
            'timestamp': datetime.now().isoformat()
        }
        
        response_format = get_response_format()
        if response_format == 'json':
            return jsonify(error_response), 500
        else:
            return format_response(error_response, response_format, 'single_rate')

@app.route('/api/rates/eur', methods=['GET'])
@rate_limit
def get_eur_rate():
    """Get EUR exchange rate from database"""
    try:
        logger.info("Fetching EUR rate from database")
        rate_data = db_service.get_currency_rate('EUR')
        
        if not rate_data:
            return jsonify({
                'error': 'Currency not found',
                'message': 'EUR exchange rate not available',
                'timestamp': datetime.now().isoformat()
            }), 404
        
        response = {
            'success': True,
            'currency': 'EUR',
            'rate': rate_data['rate'],
            'date_published': rate_data.get('date_published'),
            'last_updated': rate_data.get('updated_at'),
            'timestamp': datetime.now().isoformat(),
            'source': 'Banco Central de Venezuela (BCV) - Cached'
        }
        
        logger.info(f"Successfully fetched EUR rate: {rate_data['rate']}")
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error fetching EUR rate: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'An error occurred while fetching EUR exchange rate',
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/rates/<currency>', methods=['GET'])
@rate_limit
def get_currency_rate_endpoint(currency):
    """Get exchange rate for a specific currency from database"""
    try:
        currency = currency.upper()
        logger.info(f"Fetching {currency} rate from database")
        
        # Validate currency
        valid_currencies = ['USD', 'EUR', 'CNY', 'TRY', 'RUB']
        if currency not in valid_currencies:
            return jsonify({
                'error': 'Invalid currency',
                'message': f'Currency {currency} is not supported. Valid currencies: {", ".join(valid_currencies)}',
                'timestamp': datetime.now().isoformat()
            }), 400
        
        rate_data = db_service.get_currency_rate(currency)
        
        if not rate_data:
            return jsonify({
                'error': 'Currency not found',
                'message': f'{currency} exchange rate not available',
                'timestamp': datetime.now().isoformat()
            }), 404
        
        response = {
            'success': True,
            'currency': currency,
            'rate': rate_data['rate'],
            'date_published': rate_data.get('date_published'),
            'last_updated': rate_data.get('updated_at'),
            'timestamp': datetime.now().isoformat(),
            'source': 'Banco Central de Venezuela (BCV) - Cached'
        }
        
        logger.info(f"Successfully fetched {currency} rate: {rate_data['rate']}")
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error fetching {currency} rate: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': f'An error occurred while fetching {currency} exchange rate',
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/update', methods=['POST'])
@rate_limit
def force_update():
    """Force an immediate update from BCV website"""
    try:
        logger.info("Force update requested")
        success = db_service.force_update()
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Exchange rates updated successfully from BCV',
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to update exchange rates from BCV',
                'timestamp': datetime.now().isoformat()
            }), 503
            
    except Exception as e:
        logger.error(f"Error in force update: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'An error occurred during force update',
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get system status and recent update logs"""
    try:
        update_logs = db_service.get_update_status()
        rates_data = db_service.get_all_rates()
        
        return jsonify({
            'success': True,
            'system_status': 'operational',
            'rates_available': len(rates_data.get('rates', {})) if rates_data else 0,
            'last_update': rates_data.get('last_updated') if rates_data else None,
            'recent_updates': update_logs[:5],  # Last 5 updates
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting status: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'An error occurred while getting system status',
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'BCV Exchange Rate API with Database Cache',
        'timestamp': datetime.now().isoformat()
    })

# NEW ENHANCED ENDPOINTS

@app.route('/api/convert', methods=['GET'])
@rate_limit
@track_metrics
def currency_converter():
    """Convert amount between currencies using current BCV rates"""
    try:
        # Get parameters
        amount = request.args.get('amount', type=float)
        from_currency = request.args.get('from', '').upper()
        to_currency = request.args.get('to', '').upper()
        response_format = get_response_format()
        
        # Validation
        if not amount or amount <= 0:
            error_response = {
                'error': 'Invalid amount',
                'message': 'Please provide a valid amount greater than 0 using ?amount=100',
                'timestamp': datetime.now().isoformat()
            }
            return jsonify(error_response), 400
        
        valid_currencies = ['USD', 'EUR', 'CNY', 'TRY', 'RUB', 'VES']
        
        if not from_currency or from_currency not in valid_currencies:
            error_response = {
                'error': 'Invalid from currency',
                'message': f'Please provide a valid from currency: {", ".join(valid_currencies)}',
                'timestamp': datetime.now().isoformat()
            }
            return jsonify(error_response), 400
        
        if not to_currency or to_currency not in valid_currencies:
            error_response = {
                'error': 'Invalid to currency', 
                'message': f'Please provide a valid to currency: {", ".join(valid_currencies)}',
                'timestamp': datetime.now().isoformat()
            }
            return jsonify(error_response), 400
        
        # Same currency conversion
        if from_currency == to_currency:
            response_data = {
                'success': True,
                'conversion': {
                    'from': {'currency': from_currency, 'amount': amount},
                    'to': {'currency': to_currency, 'amount': amount},
                    'rate': 1.0,
                    'calculation': f'{amount} {from_currency} = {amount} {to_currency}'
                },
                'timestamp': datetime.now().isoformat(),
                'source': 'Direct conversion (same currency)'
            }
            return jsonify(response_data)
        
        # Get all rates for conversion
        rates_data = db_service.get_rates_with_auto_update()
        if not rates_data:
            return jsonify({
                'error': 'Conversion not available',
                'message': 'Unable to fetch current exchange rates',
                'timestamp': datetime.now().isoformat()
            }), 503
        
        rates = rates_data['rates']
        
        # Conversion logic
        if from_currency == 'VES':
            # From VES to foreign currency
            if to_currency not in rates:
                return jsonify({
                    'error': 'Currency not available',
                    'message': f'{to_currency} rate not available',
                    'timestamp': datetime.now().isoformat()
                }), 404
            
            converted_amount = amount / rates[to_currency]
            rate_used = 1 / rates[to_currency]
            calculation = f'{amount} VES ÷ {rates[to_currency]} = {converted_amount:.6f} {to_currency}'
            
        elif to_currency == 'VES':
            # From foreign currency to VES
            if from_currency not in rates:
                return jsonify({
                    'error': 'Currency not available',
                    'message': f'{from_currency} rate not available',
                    'timestamp': datetime.now().isoformat()
                }), 404
            
            converted_amount = amount * rates[from_currency]
            rate_used = rates[from_currency]
            calculation = f'{amount} {from_currency} × {rates[from_currency]} = {converted_amount:.2f} VES'
            
        else:
            # Between two foreign currencies (via VES)
            if from_currency not in rates or to_currency not in rates:
                return jsonify({
                    'error': 'Currency not available',
                    'message': 'One or both currencies not available for conversion',
                    'timestamp': datetime.now().isoformat()
                }), 404
            
            # Convert to VES first, then to target currency
            ves_amount = amount * rates[from_currency]
            converted_amount = ves_amount / rates[to_currency]
            rate_used = rates[from_currency] / rates[to_currency]
            calculation = f'{amount} {from_currency} → {ves_amount:.2f} VES → {converted_amount:.6f} {to_currency}'
        
        response_data = {
            'success': True,
            'conversion': {
                'from': {'currency': from_currency, 'amount': amount},
                'to': {'currency': to_currency, 'amount': round(converted_amount, 6)},
                'rate': round(rate_used, 6),
                'calculation': calculation
            },
            'timestamp': datetime.now().isoformat(),
            'source': 'Banco Central de Venezuela (BCV) - Cached',
            'rates_date': rates_data.get('last_updated')
        }
        
        logger.info(f"Currency conversion: {amount} {from_currency} → {converted_amount:.6f} {to_currency}")
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error in currency conversion: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'An error occurred during currency conversion',
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/compare', methods=['GET'])
@rate_limit
@track_metrics
def compare_currencies():
    """Compare multiple currencies against a base currency"""
    try:
        base_currency = request.args.get('base', 'VES').upper()
        currencies_param = request.args.get('currencies', '')
        amount = request.args.get('amount', 1, type=float)
        
        valid_currencies = ['USD', 'EUR', 'CNY', 'TRY', 'RUB', 'VES']
        
        if base_currency not in valid_currencies:
            return jsonify({
                'error': 'Invalid base currency',
                'message': f'Base currency must be one of: {", ".join(valid_currencies)}',
                'timestamp': datetime.now().isoformat()
            }), 400
        
        if currencies_param:
            currencies = [c.strip().upper() for c in currencies_param.split(',')]
            invalid_currencies = [c for c in currencies if c not in valid_currencies]
            if invalid_currencies:
                return jsonify({
                    'error': 'Invalid currencies',
                    'message': f'Invalid currencies: {", ".join(invalid_currencies)}. Valid: {", ".join(valid_currencies)}',
                    'timestamp': datetime.now().isoformat()
                }), 400
        else:
            # Default to all except base currency
            currencies = [c for c in valid_currencies if c != base_currency]
        
        # Get rates
        rates_data = db_service.get_rates_with_auto_update()
        if not rates_data:
            return jsonify({
                'error': 'Comparison not available',
                'message': 'Unable to fetch current exchange rates',
                'timestamp': datetime.now().isoformat()
            }), 503
        
        rates = rates_data['rates']
        comparisons = {}
        
        for currency in currencies:
            if currency == base_currency:
                comparisons[currency] = {
                    'rate': 1.0,
                    'converted_amount': amount,
                    'description': f'{amount} {base_currency} = {amount} {currency}'
                }
            elif base_currency == 'VES':
                # From VES to foreign currency
                if currency in rates:
                    rate = 1 / rates[currency]
                    converted = amount * rate
                    comparisons[currency] = {
                        'rate': round(rate, 6),
                        'converted_amount': round(converted, 6),
                        'description': f'{amount} VES = {converted:.6f} {currency}'
                    }
            elif currency == 'VES':
                # From foreign currency to VES
                if base_currency in rates:
                    rate = rates[base_currency]
                    converted = amount * rate
                    comparisons[currency] = {
                        'rate': rate,
                        'converted_amount': round(converted, 2),
                        'description': f'{amount} {base_currency} = {converted:.2f} VES'
                    }
            else:
                # Between two foreign currencies
                if base_currency in rates and currency in rates:
                    rate = rates[base_currency] / rates[currency]
                    converted = amount * rate
                    comparisons[currency] = {
                        'rate': round(rate, 6),
                        'converted_amount': round(converted, 6),
                        'description': f'{amount} {base_currency} = {converted:.6f} {currency}'
                    }
        
        response_data = {
            'success': True,
            'comparison': {
                'base_currency': base_currency,
                'base_amount': amount,
                'currencies': comparisons,
                'total_currencies_compared': len(comparisons)
            },
            'timestamp': datetime.now().isoformat(),
            'source': 'Banco Central de Venezuela (BCV) - Cached',
            'rates_date': rates_data.get('last_updated')
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error in currency comparison: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'An error occurred during currency comparison',
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/metrics', methods=['GET'])
@rate_limit
def get_api_metrics():
    """Get API usage metrics and statistics"""
    try:
        # Get time range (default: last 24 hours)
        hours = request.args.get('hours', 24, type=int)
        if hours < 1:
            hours = 24
        if hours > 168:  # Max 1 week
            hours = 168
            
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        # Basic metrics
        total_requests = db.session.query(func.count(ApiMetrics.id)).filter(
            ApiMetrics.created_at >= cutoff_time
        ).scalar() or 0
        
        # Requests by endpoint
        endpoint_stats = db.session.query(
            ApiMetrics.endpoint, 
            func.count(ApiMetrics.id).label('count'),
            func.avg(ApiMetrics.response_time_ms).label('avg_response_time')
        ).filter(
            ApiMetrics.created_at >= cutoff_time
        ).group_by(ApiMetrics.endpoint).all()
        
        # Requests by format
        format_stats = db.session.query(
            ApiMetrics.response_format,
            func.count(ApiMetrics.id).label('count')
        ).filter(
            ApiMetrics.created_at >= cutoff_time
        ).group_by(ApiMetrics.response_format).all()
        
        # Recent update logs
        recent_updates = db.session.query(UpdateLog).order_by(
            desc(UpdateLog.created_at)
        ).limit(5).all()
        
        response_data = {
            'success': True,
            'time_range': f'Last {hours} hours',
            'metrics': {
                'total_requests': total_requests,
                'endpoints': [
                    {
                        'endpoint': endpoint,
                        'requests': count,
                        'avg_response_time_ms': round(avg_time, 2) if avg_time else 0
                    } for endpoint, count, avg_time in endpoint_stats
                ],
                'response_formats': [
                    {'format': format_name or 'json', 'requests': count}
                    for format_name, count in format_stats
                ],
                'recent_updates': [update.to_dict() for update in recent_updates]
            },
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error fetching metrics: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'An error occurred while fetching metrics',
            'timestamp': datetime.now().isoformat()
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Not found',
        'message': 'The requested endpoint does not exist',
        'timestamp': datetime.now().isoformat()
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred',
        'timestamp': datetime.now().isoformat()
    }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
