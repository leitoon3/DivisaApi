import os
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

class ExchangeRate(db.Model):
    """Model for storing exchange rates from BCV"""
    __tablename__ = 'exchange_rates'
    
    id = db.Column(db.Integer, primary_key=True)
    currency = db.Column(db.String(3), nullable=False, index=True)  # USD, EUR, etc.
    rate = db.Column(db.Float, nullable=False)  # Exchange rate value
    date_published = db.Column(db.String(100))  # Date from BCV (as text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary for JSON responses"""
        return {
            'currency': self.currency,
            'rate': self.rate,
            'date_published': self.date_published,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<ExchangeRate {self.currency}: {self.rate}>'

class UpdateLog(db.Model):
    """Model for tracking BCV scraping updates"""
    __tablename__ = 'update_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(20), nullable=False)  # success, error
    message = db.Column(db.Text)  # Details about the update
    currencies_updated = db.Column(db.Integer, default=0)  # Number of currencies updated
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary for JSON responses"""
        return {
            'id': self.id,
            'status': self.status,
            'message': self.message,
            'currencies_updated': self.currencies_updated,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<UpdateLog {self.status}: {self.currencies_updated} currencies>'

class ExchangeRateHistory(db.Model):
    """Model for storing historical exchange rates"""
    __tablename__ = 'exchange_rate_history'
    
    id = db.Column(db.Integer, primary_key=True)
    currency = db.Column(db.String(3), nullable=False, index=True)
    rate = db.Column(db.Float, nullable=False)
    date_published = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def to_dict(self):
        return {
            'currency': self.currency,
            'rate': self.rate,
            'date_published': self.date_published,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class ApiMetrics(db.Model):
    """Model for tracking API usage metrics"""
    __tablename__ = 'api_metrics'
    
    id = db.Column(db.Integer, primary_key=True)
    endpoint = db.Column(db.String(100), nullable=False)
    method = db.Column(db.String(10), nullable=False)
    ip_address = db.Column(db.String(45))  # Support IPv6
    response_format = db.Column(db.String(10))  # json, csv, xml
    status_code = db.Column(db.Integer)
    response_time_ms = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def to_dict(self):
        return {
            'endpoint': self.endpoint,
            'method': self.method,
            'response_format': self.response_format,
            'status_code': self.status_code,
            'response_time_ms': self.response_time_ms,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }