/**
 * Cliente JavaScript para la API de tipos de cambio BCV
 * Funciona en navegadores y Node.js
 */

class BCVAPIClient {
    /**
     * Constructor del cliente
     * @param {string} baseUrl - URL base de tu API desplegada
     */
    constructor(baseUrl = 'http://localhost:5000') {
        this.baseUrl = baseUrl.replace(/\/$/, '');
        this.headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        };
    }

    /**
     * Realizar petición HTTP
     * @param {string} endpoint - Endpoint de la API
     * @param {object} options - Opciones adicionales para fetch
     * @returns {Promise<object>} Respuesta de la API
     */
    async request(endpoint, options = {}) {
        try {
            const url = `${this.baseUrl}${endpoint}`;
            const response = await fetch(url, {
                headers: this.headers,
                ...options
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            return { error: `Error conectando con API: ${error.message}` };
        }
    }

    /**
     * Obtener todas las tasas de cambio
     * @returns {Promise<object>} Todas las tasas disponibles
     */
    async getAllRates() {
        return await this.request('/api/rates');
    }

    /**
     * Obtener tasa de cambio de una divisa específica
     * @param {string} currency - Código de divisa (USD, EUR, etc.)
     * @returns {Promise<object>} Datos de la divisa
     */
    async getCurrencyRate(currency) {
        return await this.request(`/api/rates/${currency}`);
    }

    /**
     * Obtener estado del sistema
     * @returns {Promise<object>} Estado de la API
     */
    async getStatus() {
        return await this.request('/api/status');
    }

    /**
     * Forzar actualización de datos
     * @returns {Promise<object>} Resultado de la actualización
     */
    async forceUpdate() {
        return await this.request('/api/update', {
            method: 'POST'
        });
    }

    /**
     * Convertir entre divisas
     * @param {number} amount - Cantidad a convertir
     * @param {string} fromCurrency - Divisa origen
     * @param {string} toCurrency - Divisa destino
     * @returns {Promise<object>} Resultado de la conversión
     */
    async convertCurrency(amount, fromCurrency = 'VES', toCurrency = 'USD') {
        try {
            if (fromCurrency === 'VES') {
                // Convertir de bolívares a divisa extranjera
                const rateData = await this.getCurrencyRate(toCurrency);
                if (rateData.error) return rateData;

                const rate = rateData.rate;
                const converted = amount / rate;

                return {
                    original_amount: amount,
                    from_currency: fromCurrency,
                    to_currency: toCurrency,
                    exchange_rate: rate,
                    converted_amount: Math.round(converted * 100) / 100,
                    timestamp: new Date().toISOString()
                };
            } else {
                // Convertir de divisa extranjera a bolívares
                const rateData = await this.getCurrencyRate(fromCurrency);
                if (rateData.error) return rateData;

                const rate = rateData.rate;
                const converted = amount * rate;

                return {
                    original_amount: amount,
                    from_currency: fromCurrency,
                    to_currency: toCurrency,
                    exchange_rate: rate,
                    converted_amount: Math.round(converted * 100) / 100,
                    timestamp: new Date().toISOString()
                };
            }
        } catch (error) {
            return { error: `Error en conversión: ${error.message}` };
        }
    }

    /**
     * Crear calculadora de divisas en tiempo real
     * @param {string} inputId - ID del input de cantidad
     * @param {string} selectId - ID del select de divisa
     * @param {string} resultId - ID del elemento resultado
     */
    async createLiveCalculator(inputId, selectId, resultId) {
        const input = document.getElementById(inputId);
        const select = document.getElementById(selectId);
        const result = document.getElementById(resultId);

        if (!input || !select || !result) {
            console.error('Elementos no encontrados para la calculadora');
            return;
        }

        const updateCalculation = async () => {
            const amount = parseFloat(input.value) || 0;
            const currency = select.value;

            if (amount <= 0) {
                result.textContent = 'Ingresa una cantidad válida';
                return;
            }

            result.textContent = 'Calculando...';

            try {
                const conversion = await this.convertCurrency(amount, 'VES', currency);
                if (conversion.error) {
                    result.textContent = `Error: ${conversion.error}`;
                } else {
                    result.textContent = 
                        `${amount.toLocaleString()} VES = ${conversion.converted_amount.toLocaleString()} ${currency}`;
                }
            } catch (error) {
                result.textContent = `Error: ${error.message}`;
            }
        };

        input.addEventListener('input', updateCalculation);
        select.addEventListener('change', updateCalculation);

        // Cargar divisas disponibles
        try {
            const rates = await this.getAllRates();
            if (rates.success && rates.data.currencies_available) {
                select.innerHTML = rates.data.currencies_available
                    .map(currency => `<option value="${currency}">${currency}</option>`)
                    .join('');
            }
        } catch (error) {
            console.error('Error cargando divisas:', error);
        }
    }
}

// Ejemplo de uso en navegador
if (typeof window !== 'undefined') {
    // Disponible globalmente en el navegador
    window.BCVAPIClient = BCVAPIClient;
    
    // Ejemplo de inicialización
    document.addEventListener('DOMContentLoaded', async () => {
        const client = new BCVAPIClient('http://localhost:5000');
        
        console.log('=== Cliente JavaScript BCV API ===');
        
        // Ejemplo básico
        try {
            const rates = await client.getAllRates();
            console.log('Tasas actuales:', rates);
            
            const usdRate = await client.getCurrencyRate('USD');
            console.log('Tasa USD:', usdRate);
            
            const conversion = await client.convertCurrency(100, 'USD', 'VES');
            console.log('Conversión $100 USD:', conversion);
        } catch (error) {
            console.error('Error:', error);
        }
    });
}

// Ejemplo de uso en Node.js
if (typeof module !== 'undefined' && module.exports) {
    module.exports = BCVAPIClient;
    
    // Ejemplo para Node.js (requiere node-fetch)
    const example = async () => {
        const client = new BCVAPIClient('http://localhost:5000');
        
        console.log('=== Cliente Node.js BCV API ===');
        
        const rates = await client.getAllRates();
        console.log('Tasas:', rates);
    };
    
    // Ejecutar ejemplo si este archivo se ejecuta directamente
    if (require.main === module) {
        example();
    }
}