# Klubraum API

Klubraum is a app for clubs and associations to manage their members and communication. 
See https://klubraum.com for more information.

This API provides access to some functions of the API functions of Klubraum, currently only the user
management for invitation and listing of users. Its main purpose is to be integrated club memebership management
scripts to automatically add new members to Klubraum.

**Beware that the API might change without notice.**

There is also a Wordpress plugin provided by aucentiq solutions GmbH (https://aucentiq.com) to allow intergration
of single user signup with Wordpress. See: https://support.klubraum.com/admins/beitrittsanfrage_auf_vereinswebseite
(needs API token)

This API is also supporting batch invite of users using the API method which can be manually used in the frontend
of Klubraum in admin user management.

## Requirements

* Python 3.6 or higher
* requests

## Installation

Manual:

```python setup.py install```

## Usage

```python
from klubraum_api import KlubraumAPI

# login to clubraum API with a username and password
api = KlubraumAPI()
api.login(username, password)

# for some functions a user with admin permissions is needed

# if the username logged in is member of multiple klubraum instances, you can select the instance 
tenant_id = api.get_tenantid_from_name("My clubname")

# otherwise use get_tenantid() to get the tenant id of the logged in user (if is exactly one)
tenant_id = api.get_tenantid()

# get a list of users of specific tenant, if tenant is not specified, user must be admin of exactly one tenant
users = api.get_user_list(tenant_id)
# returns a list of users with the following fields:
# userId, email, name: {firstName, lastName}, userStatus, isAdmin, invitationAcceptanceDateTime, [optional] profileImageUrl

# get user profile list
api.get_user_profile_list(tenant_id)
# returns a list of users with the following fields:
# userId, tenantId, email, gender, nickName, birthdate, roles: [...], children: [...], socialMediaProfiles: [...], updateDateTime

# do a batch invite for list of emails
api.batch_invite(tenant_id, ["foo@bar.com"])

# do a public membership request for a specific email using the Klubraum App Token (like in Wordpress plugin)
token = ... # token can be generated in Klubraum App
api.membership_request_public("foo@bar.com", token)
```
