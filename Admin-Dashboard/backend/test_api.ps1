# Test script for Smart Parking Admin API
$baseUrl = "http://localhost:8000"

Write-Host "========================================" -ForegroundColor Green
Write-Host "Smart Parking Admin API Test Script" -ForegroundColor Green  
Write-Host "========================================" -ForegroundColor Green

# 1. Test health check
Write-Host "`n1. Testing health check..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "$baseUrl/health" -Method Get
    Write-Host "✓ Health check passed" -ForegroundColor Green
    Write-Host "   Status: $($health.status)" -ForegroundColor Cyan
} catch {
    Write-Host "✗ Health check failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# 2. Create entry sessions
Write-Host "`n2. Creating entry sessions..." -ForegroundColor Yellow

$entrySession1 = @{
    plateUrl = "https://res.cloudinary.com/demo/image/upload/v1234567890/plates/plate_001.jpg"
    faceUrl = "https://res.cloudinary.com/demo/image/upload/v1234567890/faces/face_001.jpg"
    gate = "In"
    faceIndex = "face_embedding_001"
    plateNumber = "29A-12345"
} | ConvertTo-Json

$entrySession2 = @{
    plateUrl = "https://res.cloudinary.com/demo/image/upload/v1234567890/plates/plate_002.jpg"
    faceUrl = "https://res.cloudinary.com/demo/image/upload/v1234567890/faces/face_002.jpg"
    gate = "In"
    faceIndex = "face_embedding_002"
    plateNumber = "30B-67890"
} | ConvertTo-Json

$entrySession3 = @{
    plateUrl = "https://res.cloudinary.com/demo/image/upload/v1234567890/plates/plate_003.jpg"
    faceUrl = "https://res.cloudinary.com/demo/image/upload/v1234567890/faces/face_003.jpg"
    gate = "In"
    faceIndex = "face_embedding_003"
    plateNumber = "51C-11111"
} | ConvertTo-Json

try {
    $result1 = Invoke-RestMethod -Uri "$baseUrl/api/sessions/" -Method Post -Body $entrySession1 -ContentType "application/json"
    Write-Host "✓ Entry session 1 created: $($result1.plateNumber)" -ForegroundColor Green
    
    $result2 = Invoke-RestMethod -Uri "$baseUrl/api/sessions/" -Method Post -Body $entrySession2 -ContentType "application/json"
    Write-Host "✓ Entry session 2 created: $($result2.plateNumber)" -ForegroundColor Green
    
    $result3 = Invoke-RestMethod -Uri "$baseUrl/api/sessions/" -Method Post -Body $entrySession3 -ContentType "application/json"
    Write-Host "✓ Entry session 3 created: $($result3.plateNumber)" -ForegroundColor Green
} catch {
    Write-Host "✗ Failed to create entry sessions: $($_.Exception.Message)" -ForegroundColor Red
}

# 3. Create exit sessions  
Write-Host "`n3. Creating exit sessions..." -ForegroundColor Yellow

$exitSession1 = @{
    plateUrl = "https://res.cloudinary.com/demo/image/upload/v1234567890/plates/plate_exit_001.jpg"
    faceUrl = "https://res.cloudinary.com/demo/image/upload/v1234567890/faces/face_exit_001.jpg"
    gate = "Out"
    faceIndex = "face_embedding_001"
    plateNumber = "29A-12345"
} | ConvertTo-Json

$exitSession2 = @{
    plateUrl = "https://res.cloudinary.com/demo/image/upload/v1234567890/plates/plate_exit_002.jpg"
    faceUrl = "https://res.cloudinary.com/demo/image/upload/v1234567890/faces/face_exit_002.jpg"
    gate = "Out"
    faceIndex = "face_embedding_002"
    plateNumber = "30B-67890"
} | ConvertTo-Json

try {
    $exitResult1 = Invoke-RestMethod -Uri "$baseUrl/api/sessions/" -Method Post -Body $exitSession1 -ContentType "application/json"
    Write-Host "✓ Exit session 1 created: $($exitResult1.plateNumber)" -ForegroundColor Green
    
    $exitResult2 = Invoke-RestMethod -Uri "$baseUrl/api/sessions/" -Method Post -Body $exitSession2 -ContentType "application/json"
    Write-Host "✓ Exit session 2 created: $($exitResult2.plateNumber)" -ForegroundColor Green
} catch {
    Write-Host "✗ Failed to create exit sessions: $($_.Exception.Message)" -ForegroundColor Red
}

# 4. Create parking slots
Write-Host "`n4. Creating parking slots..." -ForegroundColor Yellow

$slots = @(
    @{ location_code = "A01"; is_occupied = $true },
    @{ location_code = "A02"; is_occupied = $false },
    @{ location_code = "A03"; is_occupied = $true },
    @{ location_code = "B01"; is_occupied = $false },
    @{ location_code = "B02"; is_occupied = $false }
)

$slotCount = 0
foreach ($slot in $slots) {
    try {
        $slotJson = $slot | ConvertTo-Json
        $slotResult = Invoke-RestMethod -Uri "$baseUrl/api/parking/slots" -Method Post -Body $slotJson -ContentType "application/json"
        $slotCount++
        Write-Host "✓ Parking slot created: $($slot.location_code) (occupied: $($slot.is_occupied))" -ForegroundColor Green
    } catch {
        Write-Host "✗ Failed to create slot $($slot.location_code): $($_.Exception.Message)" -ForegroundColor Red
    }
}

# 5. Test all endpoints
Write-Host "`n5. Testing all endpoints..." -ForegroundColor Yellow

try {
    # Test current vehicle count
    $vehicleCount = Invoke-RestMethod -Uri "$baseUrl/api/sessions/current-vehicle-count" -Method Get
    Write-Host "✓ Current vehicles in parking: $($vehicleCount.current_vehicle_count)" -ForegroundColor Cyan
    
    # Test grouped sessions
    $groupedSessions = Invoke-RestMethod -Uri "$baseUrl/api/sessions/grouped" -Method Get
    Write-Host "✓ Total grouped sessions: $($groupedSessions.Count)" -ForegroundColor Cyan
    
    $activeCount = ($groupedSessions | Where-Object { $_.status -eq "active" }).Count
    $completedCount = ($groupedSessions | Where-Object { $_.status -eq "completed" }).Count
    Write-Host "   - Active (still parked): $activeCount" -ForegroundColor Cyan
    Write-Host "   - Completed (exited): $completedCount" -ForegroundColor Cyan
    
    # Test parking stats
    $parkingStats = Invoke-RestMethod -Uri "$baseUrl/api/parking/stats" -Method Get
    Write-Host "✓ Parking statistics:" -ForegroundColor Cyan
    Write-Host "   - Total slots: $($parkingStats.total_slots)" -ForegroundColor Cyan
    Write-Host "   - Occupied slots: $($parkingStats.occupied_slots)" -ForegroundColor Cyan
    Write-Host "   - Available slots: $($parkingStats.available_slots)" -ForegroundColor Cyan
    Write-Host "   - Current vehicles: $($parkingStats.current_vehicles)" -ForegroundColor Cyan
    Write-Host "   - Occupancy rate: $($parkingStats.occupancy_rate)%" -ForegroundColor Cyan
    
} catch {
    Write-Host "✗ Failed to test endpoints: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "Test completed!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

Write-Host "`nAPI Endpoints Summary:" -ForegroundColor Yellow
Write-Host "- GET  $baseUrl/health" -ForegroundColor White
Write-Host "- POST $baseUrl/api/sessions/" -ForegroundColor White
Write-Host "- GET  $baseUrl/api/sessions/" -ForegroundColor White
Write-Host "- GET  $baseUrl/api/sessions/grouped" -ForegroundColor White
Write-Host "- GET  $baseUrl/api/sessions/current-vehicle-count" -ForegroundColor White
Write-Host "- POST $baseUrl/api/parking/slots" -ForegroundColor White
Write-Host "- GET  $baseUrl/api/parking/slots" -ForegroundColor White
Write-Host "- GET  $baseUrl/api/parking/stats" -ForegroundColor White
