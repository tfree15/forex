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

echo -e "${ORANGE}Please enter ZKB id ${CYAN}eg.t123${ORANGE}:${NC}"
read zkbid
echo -e "${ORANGE}Please enter cif for user. Ensure leading zero are also included ${CYAN}eg:00123456${ORANGE}. cif can be obtained from IAM:
https://iam.prod.zkb.ch/plugins/pluginPage.jsf?pn=ITCRoleIdentityViewerPlugin${NC}"
read cif
echo -e "${ORANGE}Please enter user firstname:${NC}"
read firstname
echo -e "${ORANGE}Please enter user lastname:${NC}"
read lastname
while [[ ${role} != @(FXPS.ADMIN|FXPS.TRADER|FXPS.SALES|FXPS.SUPPORT) ]]
do
        echo -e "${ORANGE}Please enter user role ${CYAN}eg. FXPS.ADMIN FXPS.TRADER FXPS.SALES FXPS.SUPPORT${ORANGE}:${NC}"
        read role
done

while [[ ${group} != @(IHDH|LBCE|IHET) ]]
do
        echo -e "${ORANGE}Please enter ZKB team ${CYAN}eg. IHDH IHET LBCE${ORANGE}:${NC}"
        read group
done

echo -e "${GREEN}\nPlease verify details are correct below before confirming create."
echo -e "------------------------------------------------------------------------------------"
echo -e "${zkbid}"
echo -e "${cif}"
echo -e "${firstname}"
echo -e "${lastname}"
echo -e "${role}"
echo -e "${group}"
echo -e "------------------------------------------------------------------------------------${NC}"

while [[ ${answer} != @(Y|y|N|n) ]]
do
        echo -e "\n${ORANGE}Please confirm if above details are correct and continue to create user in London LDAP: Y/N ${NC}"
        read answer
done
if [[ ${answer} == @(Y|y) ]]
then
        # Create temporary LDIF file to create user in ldap"o
        export zkbid=${zkbid}
        export cif=${cif}
        export firstname=${firstname}
        export lastname=${lastname}
        export role=${role}
        export group=${group}

        envsubst '${zkbid},${cif},${firstname},${lastname},${role},${group}' < /usr/app/fxps/ldap/server/schema/add_new_user.tpl > /var/tmp/${zkbid}.ldif
        echo -e "${YELLOW}"
        cat /var/tmp/${zkbid}.ldif
        echo -e "${NC}"

        ldapadd -vvv -x -H ldap://localhost:389 -D  "cn=fxldapadmin,ou=funktionaleUser,ou=FX,ou=zkbRollen,o=zkb,c=ch" -W -f /var/tmp/${zkbid}.ldif
else
        echo -e "Terminating user creation."
        echo -e "\n New users are created with password \"Welcome1\". Users an change password via https://fxtrading-ld4.prod.zkb.ch:4448/"
        exit 0
fi
