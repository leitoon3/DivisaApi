import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from models import db, ExchangeRate, UpdateLog
from bcv_scraper import BCVScraper
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import desc
from config import get_config

logger = logging.getLogger(__name__)

class DatabaseService:
    """Service for managing exchange rate data in the database"""
    
    def __init__(self):
        self.scraper = BCVScraper()
        # Get update interval from configuration
        config = get_config()
        self.update_interval_minutes = config.UPDATE_INTERVAL_MINUTES
    
    def update_rates_from_bcv(self) -> bool:
        """
        Fetch latest rates from BCV and update database
        Returns True if successful, False otherwise
        """
        try:
            logger.info("Starting BCV rate update process")
            
            # Fetch data from BCV
            bcv_data = self.scraper.get_all_rates()
            
            if not bcv_data or 'rates' not in bcv_data:
                error_msg = "Failed to fetch rates from BCV website"
                logger.error(error_msg)
                self._log_update(status='error', message=error_msg)
                return False
            
            rates = bcv_data['rates']
            date_published = bcv_data.get('date', 'N/A')
            
            # Update each currency rate
            currencies_updated = 0
            for currency, rate in rates.items():
                try:
                    # Find existing rate or create new one
                    existing_rate = ExchangeRate.query.filter_by(currency=currency).first()
                    
                    if existing_rate:
                        # Update existing rate
                        existing_rate.rate = rate
                        existing_rate.date_published = date_published
                        existing_rate.updated_at = datetime.utcnow()
                        logger.info(f"Updated {currency}: {existing_rate.rate} -> {rate}")
                    else:
                        # Create new rate record
                        new_rate = ExchangeRate(
                            currency=currency,
                            rate=rate,
                            date_published=date_published
                        )
                        db.session.add(new_rate)
                        logger.info(f"Created new {currency} rate: {rate}")
                    
                    currencies_updated += 1
                    
                except SQLAlchemyError as e:
                    logger.error(f"Database error updating {currency}: {str(e)}")
                    continue
            
            # Commit all changes
            db.session.commit()
            
            success_msg = f"Successfully updated {currencies_updated} currencies"
            logger.info(success_msg)
            self._log_update(status='success', message=success_msg, currencies_updated=currencies_updated)
            
            return True
            
        except Exception as e:
            db.session.rollback()
            error_msg = f"Error updating rates from BCV: {str(e)}"
            logger.error(error_msg)
            self._log_update(status='error', message=error_msg)
            return False
    
    def get_all_rates(self) -> Optional[Dict]:
        """Get all current exchange rates from database"""
        try:
            rates = ExchangeRate.query.all()
            
            if not rates:
                logger.warning("No exchange rates found in database")
                return None
            
            # Convert to dictionary format
            rates_dict = {}
            latest_update = None
            date_published = None
            
            for rate in rates:
                rates_dict[rate.currency] = rate.rate
                
                # Track the most recent update
                if latest_update is None or rate.updated_at > latest_update:
                    latest_update = rate.updated_at
                    date_published = rate.date_published
            
            return {
                'rates': rates_dict,
                'date': date_published,
                'currencies_available': list(rates_dict.keys()),
                'base_currency': 'VES',
                'last_updated': latest_update.isoformat() if latest_update else None
            }
            
        except SQLAlchemyError as e:
            logger.error(f"Database error getting rates: {str(e)}")
            return None
    
    def get_currency_rate(self, currency: str) -> Optional[Dict]:
        """Get exchange rate for a specific currency from database"""
        try:
            currency = currency.upper()
            rate = ExchangeRate.query.filter_by(currency=currency).first()
            
            if not rate:
                logger.warning(f"Currency {currency} not found in database")
                return None
            
            return {
                'currency': rate.currency,
                'rate': rate.rate,
                'date_published': rate.date_published,
                'updated_at': rate.updated_at.isoformat() if rate.updated_at else None
            }
            
        except SQLAlchemyError as e:
            logger.error(f"Database error getting {currency} rate: {str(e)}")
            return None
    
    def should_update_rates(self) -> bool:
        """Check if rates need to be updated based on last update time"""
        try:
            # Get the most recent successful update
            last_update = UpdateLog.query.filter_by(status='success').order_by(desc(UpdateLog.created_at)).first()
            
            if not last_update:
                logger.info("No previous updates found, rates should be updated")
                return True
            
            time_since_update = datetime.utcnow() - last_update.created_at
            should_update = time_since_update > timedelta(minutes=self.update_interval_minutes)
            
            if should_update:
                logger.info(f"Last update was {time_since_update} ago, should update")
            else:
                logger.info(f"Last update was {time_since_update} ago, no update needed")
            
            return should_update
            
        except SQLAlchemyError as e:
            logger.error(f"Database error checking update time: {str(e)}")
            return True  # If we can't check, assume we should update
    
    def get_rates_with_auto_update(self) -> Optional[Dict]:
        """Get rates from database, updating from BCV if necessary"""
        try:
            # Check if we need to update
            if self.should_update_rates():
                logger.info("Rates are outdated, updating from BCV...")
                update_success = self.update_rates_from_bcv()
                
                if not update_success:
                    logger.warning("BCV update failed, returning cached rates")
            
            # Return rates from database
            return self.get_all_rates()
            
        except Exception as e:
            logger.error(f"Error in get_rates_with_auto_update: {str(e)}")
            return None
    
    def get_update_status(self) -> List[Dict]:
        """Get recent update logs"""
        try:
            logs = UpdateLog.query.order_by(desc(UpdateLog.created_at)).limit(10).all()
            return [log.to_dict() for log in logs]
            
        except SQLAlchemyError as e:
            logger.error(f"Database error getting update logs: {str(e)}")
            return []
    
    def _log_update(self, status: str, message: str, currencies_updated: int = 0):
        """Log an update attempt to the database"""
        try:
            log = UpdateLog(
                status=status,
                message=message,
                currencies_updated=currencies_updated
            )
            db.session.add(log)
            db.session.commit()
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to log update: {str(e)}")
            db.session.rollback()
    
    def force_update(self) -> bool:
        """Force an immediate update from BCV regardless of timing"""
        logger.info("Forcing immediate update from BCV")
        return self.update_rates_from_bcv()