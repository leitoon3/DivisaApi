#!/usr/bin/env python3
"""
Ejemplo de cliente Python para consumir la API de tipos de cambio BCV
"""

import requests
import json
from datetime import datetime

class BCVAPIClient:
    """Cliente Python para la API de tipos de cambio BCV"""
    
    def __init__(self, base_url="http://localhost:5000"):
        """
        Inicializar cliente
        
        Args:
            base_url (str): URL base de tu API desplegada
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'BCV-API-Client-Python/1.0',
            'Accept': 'application/json'
        })
    
    def get_all_rates(self):
        """Obtener todas las tasas de cambio"""
        try:
            response = self.session.get(f"{self.base_url}/api/rates")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": f"Error conectando con API: {str(e)}"}
    
    def get_currency_rate(self, currency):
        """
        Obtener tasa de cambio de una divisa específica
        
        Args:
            currency (str): Código de divisa (USD, EUR, etc.)
        """
        try:
            response = self.session.get(f"{self.base_url}/api/rates/{currency}")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": f"Error obteniendo {currency}: {str(e)}"}
    
    def convert_currency(self, amount, from_currency="VES", to_currency="USD"):
        """
        Convertir entre divisas
        
        Args:
            amount (float): Cantidad a convertir
            from_currency (str): Divisa origen
            to_currency (str): Divisa destino
        """
        if from_currency == "VES":
            # Convertir de bolívares a divisa extranjera
            rate_data = self.get_currency_rate(to_currency)
            if "error" in rate_data:
                return rate_data
            
            rate = rate_data.get("rate")
            converted = amount / rate
            
            return {
                "original_amount": amount,
                "from_currency": from_currency,
                "to_currency": to_currency,
                "exchange_rate": rate,
                "converted_amount": round(converted, 2),
                "timestamp": datetime.now().isoformat()
            }
        else:
            # Convertir de divisa extranjera a bolívares
            rate_data = self.get_currency_rate(from_currency)
            if "error" in rate_data:
                return rate_data
            
            rate = rate_data.get("rate")
            converted = amount * rate
            
            return {
                "original_amount": amount,
                "from_currency": from_currency,
                "to_currency": to_currency,
                "exchange_rate": rate,
                "converted_amount": round(converted, 2),
                "timestamp": datetime.now().isoformat()
            }

# Ejemplo de uso
if __name__ == "__main__":
    # Cambiar por la URL de tu servidor desplegado
    client = BCVAPIClient("http://localhost:5000")
    
    print("=== API de Tipos de Cambio BCV - Cliente Python ===\n")
    
    # Obtener todas las tasas
    print("1. Todas las tasas actuales:")
    all_rates = client.get_all_rates()
    if "error" not in all_rates and all_rates.get("success"):
        rates = all_rates["data"]["rates"]
        for currency, rate in rates.items():
            print(f"   {currency}: {rate:,.2f} VES")
        print(f"   Última actualización: {all_rates['data'].get('last_updated', 'N/A')}")
    else:
        print(f"   Error: {all_rates.get('error', 'Error desconocido')}")
    
    print("\n2. Tasa específica del dólar:")
    usd_rate = client.get_currency_rate("USD")
    if "error" not in usd_rate and usd_rate.get("success"):
        print(f"   1 USD = {usd_rate['rate']:,.2f} VES")
    else:
        print(f"   Error: {usd_rate.get('error', 'Error desconocido')}")
    
    print("\n3. Conversiones de ejemplo:")
    # Convertir $100 USD a bolívares
    conversion = client.convert_currency(100, "USD", "VES")
    if "error" not in conversion:
        print(f"   $100 USD = {conversion['converted_amount']:,.2f} VES")
    
    # Convertir 1,000,000 VES a dólares
    conversion = client.convert_currency(1000000, "VES", "USD")
    if "error" not in conversion:
        print(f"   1,000,000 VES = ${conversion['converted_amount']:,.2f} USD")