#!/usr/bin/env python3
"""
App de demostración - Calculadora de Tipos de Cambio BCV
Muestra cómo integrar la API en una aplicación real
"""

import requests
import time
import json
from datetime import datetime

class CurrencyConverter:
    """Aplicación de conversión de divisas usando la API BCV"""
    
    def __init__(self, api_url="http://localhost:5000"):
        self.api_url = api_url
        self.session = requests.Session()
        self.cached_rates = {}
        self.last_update = None
        
    def get_rates(self):
        """Obtener tasas con cache inteligente"""
        # Si tenemos cache reciente (menos de 5 minutos), usarlo
        if self.cached_rates and self.last_update:
            time_since_update = time.time() - self.last_update
            if time_since_update < 300:  # 5 minutos
                print("📁 Usando cache local...")
                return self.cached_rates
        
        try:
            print("🌐 Consultando API...")
            response = self.session.get(f"{self.api_url}/api/rates")
            
            if response.status_code == 429:
                print("⏳ Rate limit alcanzado, esperando...")
                time.sleep(11)  # Esperar un poco más que el límite
                response = self.session.get(f"{self.api_url}/api/rates")
            
            response.raise_for_status()
            data = response.json()
            
            if data.get('success'):
                self.cached_rates = data['data']['rates']
                self.last_update = time.time()
                print("✅ Tasas actualizadas desde la API")
                return self.cached_rates
            else:
                print("❌ Error en respuesta de la API")
                return None
                
        except requests.RequestException as e:
            print(f"❌ Error conectando con API: {e}")
            return self.cached_rates if self.cached_rates else None
    
    def convert_currency(self, amount, from_currency, to_currency):
        """Convertir entre divisas"""
        rates = self.get_rates()
        if not rates:
            return None
        
        if from_currency == 'VES':
            if to_currency not in rates:
                return None
            return amount / rates[to_currency]
        elif to_currency == 'VES':
            if from_currency not in rates:
                return None
            return amount * rates[from_currency]
        else:
            # Conversión entre dos divisas extranjeras vía VES
            if from_currency not in rates or to_currency not in rates:
                return None
            ves_amount = amount * rates[from_currency]
            return ves_amount / rates[to_currency]
    
    def format_number(self, number):
        """Formatear número con separadores de miles"""
        return f"{number:,.2f}"
    
    def display_rates(self):
        """Mostrar todas las tasas actuales"""
        rates = self.get_rates()
        if not rates:
            print("No se pudieron obtener las tasas")
            return
        
        print("\n" + "="*50)
        print("💱 TASAS DE CAMBIO ACTUALES BCV")
        print("="*50)
        
        for currency, rate in rates.items():
            symbols = {
                'USD': '$', 'EUR': '€', 'CNY': '¥', 
                'TRY': '₺', 'RUB': '₽'
            }
            symbol = symbols.get(currency, currency)
            print(f"  {symbol} 1 {currency} = {self.format_number(rate)} VES")
        
        print("="*50)
    
    def interactive_converter(self):
        """Calculadora interactiva"""
        print("\n🧮 CALCULADORA DE DIVISAS")
        print("Escribe 'salir' para terminar\n")
        
        currencies = ['VES', 'USD', 'EUR', 'CNY', 'TRY', 'RUB']
        
        while True:
            try:
                # Obtener cantidad
                amount_input = input("💰 Cantidad a convertir: ").strip()
                if amount_input.lower() in ['salir', 'exit', 'quit']:
                    break
                
                amount = float(amount_input)
                if amount <= 0:
                    print("❌ La cantidad debe ser mayor a 0")
                    continue
                
                # Obtener divisa origen
                print("Divisas disponibles:", ", ".join(currencies))
                from_curr = input("📤 Divisa origen: ").strip().upper()
                if from_curr not in currencies:
                    print("❌ Divisa no válida")
                    continue
                
                # Obtener divisa destino
                to_curr = input("📥 Divisa destino: ").strip().upper()
                if to_curr not in currencies:
                    print("❌ Divisa no válida")
                    continue
                
                if from_curr == to_curr:
                    print(f"💡 {self.format_number(amount)} {from_curr}")
                    continue
                
                # Realizar conversión
                result = self.convert_currency(amount, from_curr, to_curr)
                if result is None:
                    print("❌ No se pudo realizar la conversión")
                    continue
                
                # Mostrar resultado
                print(f"✅ {self.format_number(amount)} {from_curr} = {self.format_number(result)} {to_curr}")
                print()
                
            except ValueError:
                print("❌ Cantidad inválida. Use números como 100 o 1500.50")
            except KeyboardInterrupt:
                print("\n👋 ¡Hasta luego!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def price_alerts(self):
        """Simulación de alertas de precio"""
        print("\n🔔 SIMULACIÓN DE ALERTAS")
        
        target_usd = 130.0  # Alerta si USD pasa de 130 VES
        
        rates = self.get_rates()
        if rates and 'USD' in rates:
            current_usd = rates['USD']
            print(f"💵 Precio actual USD: {self.format_number(current_usd)} VES")
            print(f"🎯 Alerta configurada: > {self.format_number(target_usd)} VES")
            
            if current_usd > target_usd:
                print("🚨 ¡ALERTA! El dólar superó el precio objetivo")
            else:
                diff = target_usd - current_usd
                print(f"📊 Faltan {self.format_number(diff)} VES para la alerta")

def main():
    """Función principal de la aplicación"""
    print("🏛️ DEMO: Integración con API de Tipos de Cambio BCV")
    print("=" * 60)
    
    converter = CurrencyConverter()
    
    while True:
        print("\n📋 MENÚ PRINCIPAL:")
        print("1. Ver tasas actuales")
        print("2. Calculadora de conversión")
        print("3. Simulación de alertas")
        print("4. Salir")
        
        choice = input("\n👉 Selecciona una opción (1-4): ").strip()
        
        try:
            if choice == '1':
                converter.display_rates()
                
            elif choice == '2':
                converter.interactive_converter()
                
            elif choice == '3':
                converter.price_alerts()
                
            elif choice == '4':
                print("👋 ¡Gracias por usar la demo!")
                break
                
            else:
                print("❌ Opción inválida. Escoge 1, 2, 3 o 4")
                
        except KeyboardInterrupt:
            print("\n👋 ¡Hasta luego!")
            break
        except Exception as e:
            print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    main()