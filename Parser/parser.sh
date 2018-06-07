#!/bin/bash

#curl -k https://coinmarketcap.com/tokens/views/all/ |
cat index.html |
grep -A2 'currency-name-container\|https://etherscan.io/token' |
grep -B2 -A2 '/currencies/ethereum' |
#head -50 |
tr -d '\n' |
sed 's/<a class="currency-name-container" href="\([^"]*\)">/\n\1;/g' |
sed 's/<.*https:\/\/etherscan.io\/token\//;/g' |
sed 's/" target=.*//g' |
while IFS=';' read -r var1 var2 var3 ;
do
    if [[ "${var3}" != "" ]];
    then

    if [[ "${var3:0:2}" != "0x" ]]; 
    then
	number=$RANDOM
	let "number %= 15"
	sleep $number
	ethAddress="$(curl -k https://coinmarketcap.com${var1} 2>/dev/null | grep 'https://ethplorer.io/address/' | sed 's/.*https:\/\/ethplorer.io\/address\/\([^"]*\)".*/\1/g')"
	[[ "${ethAddress:0:2}" = "0x" ]] && echo "$var2|$ethAddress"
#	echo "$var2|curl -k https://coinmarketcap.com${var1} "
    else
	echo "$var2|$var3"
    fi
    fi
done

