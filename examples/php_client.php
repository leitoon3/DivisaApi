<?php
/**
 * Cliente PHP para la API de tipos de cambio BCV
 * Compatible con PHP 7.4+
 */

class BCVAPIClient {
    private $baseUrl;
    private $timeout;
    
    /**
     * Constructor
     * @param string $baseUrl URL base de tu API desplegada
     * @param int $timeout Timeout en segundos
     */
    public function __construct($baseUrl = 'http://localhost:5000', $timeout = 30) {
        $this->baseUrl = rtrim($baseUrl, '/');
        $this->timeout = $timeout;
    }
    
    /**
     * Realizar petición HTTP
     * @param string $endpoint Endpoint de la API
     * @param string $method Método HTTP
     * @param array $data Datos para enviar
     * @return array Respuesta de la API
     */
    private function request($endpoint, $method = 'GET', $data = null) {
        $url = $this->baseUrl . $endpoint;
        
        $options = [
            'http' => [
                'method' => $method,
                'header' => [
                    'Accept: application/json',
                    'Content-Type: application/json',
                    'User-Agent: BCV-API-Client-PHP/1.0'
                ],
                'timeout' => $this->timeout
            ]
        ];
        
        if ($data && $method === 'POST') {
            $options['http']['content'] = json_encode($data);
        }
        
        $context = stream_context_create($options);
        $response = @file_get_contents($url, false, $context);
        
        if ($response === false) {
            return ['error' => 'Error conectando con la API'];
        }
        
        $decoded = json_decode($response, true);
        return $decoded ?: ['error' => 'Respuesta inválida de la API'];
    }
    
    /**
     * Obtener todas las tasas de cambio
     * @return array
     */
    public function getAllRates() {
        return $this->request('/api/rates');
    }
    
    /**
     * Obtener tasa de cambio de una divisa específica
     * @param string $currency Código de divisa
     * @return array
     */
    public function getCurrencyRate($currency) {
        return $this->request('/api/rates/' . strtoupper($currency));
    }
    
    /**
     * Obtener estado del sistema
     * @return array
     */
    public function getStatus() {
        return $this->request('/api/status');
    }
    
    /**
     * Forzar actualización
     * @return array
     */
    public function forceUpdate() {
        return $this->request('/api/update', 'POST');
    }
    
    /**
     * Convertir entre divisas
     * @param float $amount Cantidad a convertir
     * @param string $fromCurrency Divisa origen
     * @param string $toCurrency Divisa destino
     * @return array
     */
    public function convertCurrency($amount, $fromCurrency = 'VES', $toCurrency = 'USD') {
        if ($fromCurrency === 'VES') {
            // Convertir de bolívares a divisa extranjera
            $rateData = $this->getCurrencyRate($toCurrency);
            if (isset($rateData['error'])) {
                return $rateData;
            }
            
            $rate = $rateData['rate'];
            $converted = $amount / $rate;
            
            return [
                'original_amount' => $amount,
                'from_currency' => $fromCurrency,
                'to_currency' => $toCurrency,
                'exchange_rate' => $rate,
                'converted_amount' => round($converted, 2),
                'timestamp' => date('c')
            ];
        } else {
            // Convertir de divisa extranjera a bolívares
            $rateData = $this->getCurrencyRate($fromCurrency);
            if (isset($rateData['error'])) {
                return $rateData;
            }
            
            $rate = $rateData['rate'];
            $converted = $amount * $rate;
            
            return [
                'original_amount' => $amount,
                'from_currency' => $fromCurrency,
                'to_currency' => $toCurrency,
                'exchange_rate' => $rate,
                'converted_amount' => round($converted, 2),
                'timestamp' => date('c')
            ];
        }
    }
    
    /**
     * Formatear número como moneda
     * @param float $amount
     * @param string $currency
     * @return string
     */
    public function formatCurrency($amount, $currency = 'VES') {
        $symbols = [
            'USD' => '$',
            'EUR' => '€',
            'VES' => 'Bs.',
            'CNY' => '¥',
            'TRY' => '₺',
            'RUB' => '₽'
        ];
        
        $symbol = $symbols[$currency] ?? $currency;
        return $symbol . number_format($amount, 2, ',', '.');
    }
}

// Ejemplo de uso
if (basename(__FILE__) == basename($_SERVER['PHP_SELF'])) {
    echo "=== API de Tipos de Cambio BCV - Cliente PHP ===\n\n";
    
    // Cambiar por la URL de tu servidor desplegado
    $client = new BCVAPIClient('http://localhost:5000');
    
    // 1. Obtener todas las tasas
    echo "1. Todas las tasas actuales:\n";
    $allRates = $client->getAllRates();
    if (isset($allRates['error'])) {
        echo "   Error: " . $allRates['error'] . "\n";
    } elseif ($allRates['success']) {
        $rates = $allRates['data']['rates'];
        foreach ($rates as $currency => $rate) {
            echo "   $currency: " . number_format($rate, 2, ',', '.') . " VES\n";
        }
        echo "   Última actualización: " . ($allRates['data']['last_updated'] ?? 'N/A') . "\n";
    }
    
    // 2. Tasa específica
    echo "\n2. Tasa específica del dólar:\n";
    $usdRate = $client->getCurrencyRate('USD');
    if (!isset($usdRate['error']) && $usdRate['success']) {
        echo "   1 USD = " . number_format($usdRate['rate'], 2, ',', '.') . " VES\n";
    } else {
        echo "   Error: " . ($usdRate['error'] ?? 'Error desconocido') . "\n";
    }
    
    // 3. Conversiones
    echo "\n3. Conversiones de ejemplo:\n";
    
    // $100 USD a VES
    $conversion = $client->convertCurrency(100, 'USD', 'VES');
    if (!isset($conversion['error'])) {
        echo "   $100 USD = " . $client->formatCurrency($conversion['converted_amount'], 'VES') . "\n";
    }
    
    // 1,000,000 VES a USD
    $conversion = $client->convertCurrency(1000000, 'VES', 'USD');
    if (!isset($conversion['error'])) {
        echo "   Bs.1,000,000 = " . $client->formatCurrency($conversion['converted_amount'], 'USD') . "\n";
    }
    
    // 4. Estado del sistema
    echo "\n4. Estado del sistema:\n";
    $status = $client->getStatus();
    if (isset($status['success']) && $status['success']) {
        echo "   Estado: " . $status['system_status'] . "\n";
        echo "   Divisas disponibles: " . $status['rates_available'] . "\n";
        echo "   Última actualización: " . ($status['last_update'] ?? 'N/A') . "\n";
    }
}