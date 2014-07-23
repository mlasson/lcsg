echo "pushing locally ..."
git push
echo "pulling remotely ..."
ssh vitrine.ovh 'sh -c "cd srv/lcsg/ && ls && git pull"'
