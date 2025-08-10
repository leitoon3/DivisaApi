#!/bin/bash
# Script de prueba para demostrar los múltiples formatos de respuesta

API_URL="http://localhost:5000"
DELAY=11  # Delay para evitar rate limiting

echo "🧪 PRUEBAS DE FORMATOS DE RESPUESTA - API BCV"
echo "=============================================="
echo ""

# Test 1: JSON (por defecto)
echo "📋 1. JSON (formato por defecto)"
echo "Comando: curl \"$API_URL/api/rates/usd\""
curl -s "$API_URL/api/rates/usd"
echo -e "\n"

sleep $DELAY

# Test 2: CSV con parámetro
echo "📊 2. CSV usando parámetro ?format=csv"  
echo "Comando: curl \"$API_URL/api/rates/usd?format=csv\""
curl -s "$API_URL/api/rates/usd?format=csv"
echo -e "\n"

sleep $DELAY

# Test 3: XML con parámetro
echo "📄 3. XML usando parámetro ?format=xml"
echo "Comando: curl \"$API_URL/api/rates/usd?format=xml\""
curl -s "$API_URL/api/rates/usd?format=xml"
echo -e "\n"

sleep $DELAY

# Test 4: CSV con Accept header
echo "📊 4. CSV usando Accept header"
echo "Comando: curl -H \"Accept: text/csv\" \"$API_URL/api/rates/eur\""
curl -s -H "Accept: text/csv" "$API_URL/api/rates/eur"
echo -e "\n"

sleep $DELAY

# Test 5: XML con Accept header  
echo "📄 5. XML usando Accept header"
echo "Comando: curl -H \"Accept: application/xml\" \"$API_URL/api/rates/eur\""
curl -s -H "Accept: application/xml" "$API_URL/api/rates/eur"
echo -e "\n"

sleep $DELAY

# Test 6: Todas las tasas en CSV
echo "📊 6. Todas las tasas en formato CSV"
echo "Comando: curl \"$API_URL/api/rates?format=csv\""
curl -s "$API_URL/api/rates?format=csv"
echo -e "\n"

sleep $DELAY

# Test 7: Todas las tasas en XML
echo "📄 7. Todas las tasas en formato XML"
echo "Comando: curl \"$API_URL/api/rates?format=xml\""
curl -s "$API_URL/api/rates?format=xml"
echo -e "\n"

echo "✅ PRUEBAS COMPLETADAS"
echo "====================="
echo ""
echo "💡 NOTAS:"
echo "- JSON es el formato por defecto"
echo "- CSV es ideal para Excel y análisis de datos"
echo "- XML es ideal para sistemas empresariales"
echo "- Todos los endpoints soportan los tres formatos"
echo "- Rate limiting de 10 segundos por IP aplica a todos los formatos"