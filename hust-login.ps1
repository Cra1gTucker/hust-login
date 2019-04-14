Invoke-Webrequest -Uri http://123.123.123.123 -TimeoutSec 3
if($?){
    $info = (Invoke-Webrequest -Uri http://123.123.123.123)
}
else{
    Write-Host "Failed to get redirect info."
    exit
}
$info.RawContent -match "http://.+eportal/"
$url = $Matches.0 + 'InterFace.do?method=login'
$info.RawContent -match "wlan[^']+"
$qs = $Matches.0
$ecqs = [uri]::EscapeDataString($qs)
$user = Read-Host 'Username'
$pass = Read-Host 'Password' -AsSecureString
$postParams = @{userId=$user;password=[Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($pass));service='';queryString=$ecqs;operatorPwd='';validcode='';passwordEncrypt='false'}
$response = (Invoke-Webrequest -Uri $url -Method POST -Body $postParams)
Write-Host $response
pause