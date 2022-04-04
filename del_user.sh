#!/bin/bash

b='\e[1m'
u='\e[4m'
RST='\e[0m'
RED='\e[38;5;196m'
YELLOW='\e[38;5;226m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
ORANGE='\e[38;5;208m'
NC='\033[0m' # No Color

role=""
group=""
answer=""

echo -e "${YELLOW}\nDelete London LDAP user script"
echo -e "${ORANGE}\nPlease enter ZKB id to delete ${CYAN}eg.t123${ORANGE}:${NC}"
read zkbid

ldapsearch -LLL -xZ -h localhost:389 -b "o=zkb,c=ch"|grep -A1 "uid: ${zkbid}"|egrep 'principalPtr|dn'

echo -e "${ORANGE}From above please enter cif for user? Ensure leading zero are also included ${CYAN}eg:00123456${ORANGE}:${NC}".
read cif

ldapsearch -LLL -xZ -h localhost:389 -b "ou=FXPriceStar,ou=FX,ou=zkbRollen,o=zkb,c=ch" "(uniquemember=zkbCifNr=${cif},ou=zkbpartner,o=zkb,c=ch)"

echo -e "${ORANGE}From above enter user role ${CYAN}eg. FXPS.ADMIN FXPS.TRADER FXPS.SALES FXPS.SUPPORT${ORANGE}:${NC}"
read role

echo -e "${GREEN}\nPlease verify details are correct below before confirming delete."
echo -e "------------------------------------------------------------------------------------"
echo -e "${zkbid}"
echo -e "${cif}"
echo -e "${role}"
echo -e "------------------------------------------------------------------------------------${NC}"

while [[ ${answer} != @(Y|y|N|n) ]]
do
        echo -e "\n${ORANGE}Please confirm if above details are correct and continue to delete user in London LDAP: Y/N ${NC}"
        read answer
done
if [[ ${answer} == @(Y|y) ]]
then
        # Create temporary LDIF file to delete user in ldap"
        export zkbid=${zkbid}
        export cif=${cif}
        export role=${role}

        envsubst '${zkbid},${cif},${role}' < /usr/app/fxps/ldap/server/schema/unique_del.tpl > /var/tmp/unique_del_${zkbid}.ldif
        echo -e "${YELLOW}"
        cat /var/tmp/unique_del_${zkbid}.ldif
        echo -e "${NC}"

        echo -e "${GREEN}Deleting user from FXPS role ...${NC}"
        ldapmodify -vvv -x -H ldap://localhost:389 -D  "cn=fxldapadmin,ou=funktionaleUser,ou=FX,ou=zkbRollen,o=zkb,c=ch" -W -f /var/tmp/unique_del_${zkbid}.ldif
        echo -e "${GREEN}\nDeleting user from local ZKB LDAP ...${NC}"
        ldapdelete -v -H ldap://localhost:389 -c -D "cn=fxldapadmin,ou=funktionaleUser,ou=FX,ou=zkbRollen,o=zkb,c=ch" -W uid=${zkbid},ou=user,ou=FX,ou=zkbRollen,o=zkb,c=ch
        echo -e "${GREEN}\nDeleting user CIF from ZKB LDAP ...${NC}"
        ldapdelete -v -H ldap://localhost:389 -D "cn=fxldapadmin,ou=funktionaleUser,ou=FX,ou=zkbRollen,o=zkb,c=ch" -W zkbCifNr=${cif},ou=zkbPartner,o=zkb,c=ch

else
        echo -e "Terminating user creation."
        exit 0
fi
