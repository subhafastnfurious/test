# officebird.com


Office Bird is an app facilitating subletting of office space between landlords
and potential tenants.

Landlord creates buildings, and tenants browse and participate in the ones they find
interesting

# local API development

    ln -s ../../pre-commit.hook.py .git/hooks/pre-commit
    apt install postgres
    sudo su postgres -c "createuser -s $USER"
    createdb ob
    mkvirtualenv -r backend/requirements.txt -p/usr/bin/python3.6 venv
    cd backend
    # TODO: describe the initial setup, explain how to migrate, run tests and start API
