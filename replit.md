# Overview

This is a Flask-based web API with PostgreSQL database caching that provides exchange rates from the Banco Central de Venezuela (BCV). The application intelligently caches scraped currency exchange rates in a database, serving fast responses to clients while automatically updating data every 30 minutes. The API supports multiple response formats (JSON, CSV, XML) for maximum integration flexibility, with comprehensive CURL examples and client libraries for Python, JavaScript, and PHP. This architecture prevents overloading the BCV server and provides reliable, fast API responses for production deployment.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture
- **Template Engine**: Flask's Jinja2 templating system
- **UI Framework**: Bootstrap with dark theme for responsive design
- **Icons**: Feather Icons for visual elements
- **Interactivity**: Vanilla JavaScript for API interactions and live rate updates
- **Styling**: Custom CSS for enhanced user experience with hover effects and responsive design

## Backend Architecture
- **Web Framework**: Flask with WSGI application structure
- **Database**: PostgreSQL with SQLAlchemy ORM for data persistence
- **Caching System**: Intelligent database caching with automatic 30-minute refresh intervals
- **Web Scraping**: Custom BCVScraper class using requests and BeautifulSoup4
- **Rate Limiting**: IP-based rate limiting with 10-second intervals to prevent client abuse
- **Database Service**: Centralized service managing cache updates, data retrieval, and BCV synchronization
- **Multiple Response Formats**: Support for JSON, CSV, and XML output formats via query parameters or Accept headers
- **Content Negotiation**: Automatic format detection from request parameters (?format=) or Accept headers
- **Error Handling**: Comprehensive logging and exception handling for both scraping and database operations
- **Session Management**: Persistent HTTP sessions for efficient web scraping
- **Proxy Support**: ProxyFix middleware for handling reverse proxy headers

## Data Processing
- **HTML Parsing**: BeautifulSoup4 for extracting currency rates from BCV website
- **Data Validation**: Type hints and optional return types for robust data handling
- **Currency Mapping**: Flexible currency identification system supporting multiple currencies (USD, EUR, etc.)
- **Database Models**: ExchangeRate and UpdateLog models for tracking currency data and system operations
- **Automated Updates**: Intelligent caching with 30-minute refresh intervals to balance freshness with performance
- **Fallback Strategy**: Graceful degradation serving cached data when BCV is unavailable

## Security & Performance
- **Rate Limiting**: Per-IP request throttling to protect both the application and BCV servers
- **User Agent Spoofing**: Proper browser headers to ensure successful web scraping
- **Timeout Handling**: 30-second timeout for external requests
- **Error Recovery**: Graceful handling of network failures and parsing errors

# External Dependencies

## Web Scraping Target
- **Banco Central de Venezuela (BCV)**: Official source for Venezuelan exchange rates at https://www.bcv.org.ve/

## Python Libraries
- **Flask**: Web application framework for API and frontend serving
- **requests**: HTTP library for web scraping operations
- **BeautifulSoup4**: HTML parsing and data extraction from BCV website
- **Werkzeug**: WSGI utilities including ProxyFix middleware

## Frontend Dependencies
- **Bootstrap**: CSS framework loaded via CDN for responsive UI design
- **Feather Icons**: Icon library for consistent visual elements
- **Replit Bootstrap Theme**: Custom dark theme for improved aesthetics

## Infrastructure
- **WSGI Server**: Compatible with standard WSGI deployment (Gunicorn, uWSGI, etc.)
- **Environment Variables**: Configurable session secrets and deployment settings
- **Logging**: Python's built-in logging framework for debugging and monitoring