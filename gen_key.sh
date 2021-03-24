DER=$(mktemp)
chmod 0600 $DER
openssl asn1parse -genconf pubkey_fix_exp.asn1 -out $DER -noout
openssl rsa -in $DER -inform der -pubin -out pubkey_fix_exp.pem
rm $DER
openssl rsa -pubin -in pubkey_fix_exp.pem -text -noout
