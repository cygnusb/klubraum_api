import json
import requests


class KlubraumApiException(Exception):
	pass


class KlubraumApi:
	API_BASE_URL = "https://api.klubraum.com"
	API_PREFIX = "api-v"

	def __init__(self):
		self.api_version = "1"
		self.base_url = "%s/%s%s" % (self.API_BASE_URL, self.API_PREFIX, self.api_version)
		self.auth_token = None
		self.login_done = False
		self.user_summary = None

	@property
	def tenants(self):
		return self.user_summary["tenants"]

	@property
	def memberships(self):
		return self.user_summary["memberships"]

	@property
	def user_memberships(self):
		return self.user_summary["user"]["memberships"]

	def __check_status_code(self,r):
		if r.status_code == 401:
			msg = r.json()["message"]
			raise KlubraumApiException("Request ailed with message %s", msg)
		if r.status_code == 429:
			raise KlubraumApiException("Request failed with too many requests")
		if r.status_code != 200:
			raise KlubraumApiException("Request failed with status code %s", r.status_code)

	def login(self, user, password):
		url = "%s/user/password/login" % self.base_url
		data = {
			"loginId": user,
			"password": password
		}
		headers = {"Content-Type": "application/json"}
		r = requests.post(url, json=data, headers=headers)
		self.__check_status_code(r)
		self.auth_token = r.json()["authToken"]
		self.login_done = True
		self.user_current_summary()

	def get_auth_token(self):
		return self.auth_token

	# select the club (tenant) to work with by name
	def get_tenantid_from_name(self, tenant_name):
		for k, v in self.tenants.items():
			if v == tenant_name:
				return k
		return None

	# if user is only member of one club, return the tenant_id of that club
	def get_tenantid(self):
		if self.tenants and len(self.tenants) == 1:
			return list(self.tenants.keys())[0]
		raise KlubraumApiException("User is member of more than one club - use get_tenantid_from_name() to select a club")

	# get the current user summary
	def user_current_summary(self):
		# /user/current/summary returns a summary of the current user
		headers = {"X-Api-Version": self.api_version, "X-Auth-Token": self.auth_token}
		url = "%s/user/current/summary" % self.base_url
		r = requests.get(url, headers=headers)
		self.__check_status_code(r)
		# returns a summary of the current user with the following fields:
		# user: {userId, email, name: {firstName, lastName}, memberships: {tenantId: [role, ]}, userStatus: [string] "Active", authSeq: [integer] 0
		# tenants: {tenantId: tenantName, ...}
		# memberships: { tenantId: {tenantName: [string] name, tenantStatus: [string] "Active"},...}
		# invitations: [],
		# membershipRequests: []
		assert self.login_done
		self.user_summary = r.json()
		return self.user_summary

	# get a list of all users for a specific klubraum tenant-id
	def get_user_list(self, tenant_id=None):
		assert self.login_done
		if not tenant_id:
			tenant_id = self.get_tenantid()
		assert tenant_id in self.tenants
		url = "%s/user/list?tenantId=%s" % (self.base_url, tenant_id)
		r = requests.get(url, headers={"X-Api-Version": self.api_version, "X-Auth-Token": self.auth_token})
		self.__check_status_code(r)
		# returns a list of users with the following fields:
		# userId, email, name: {firstName, lastName}, userStatus, isAdmin, invitationAcceptanceDateTime, [optional] profileImageUrl
		user_list = r.json()
		return user_list

	def get_user_profile_list(self, tenant_id=None):
		# /user/profile/list?tenantId=7911c7d9-6c3c-4feb-a004-661ec0373b87&updateDateTime=2023-01-05T15%3A25%3A30.494Z
		# returns a list of users with the following fields:
		# userId, tenantId, email, gender, nickName, birthdate
		# roles: []
		# children: []
		# socialMediaProfiles: []
		# updateDateTime
		assert self.login_done
		if tenant_id is None:
			tenant_id = self.get_tenantid()
		assert tenant_id in self.tenants
		url = "%s/user/profile/list?tenantId=%s" % (self.base_url, tenant_id)
		headers = {"X-Api-Version": self.api_version, "X-Auth-Token": self.auth_token}
		r = requests.get(url, headers=headers)
		self.__check_status_code(r)
		user_profile_list = r.json()
		return user_profile_list

	def membership_request_public(self, email, token):
		# function creates a membership request using a public token (wordpress plugin)
		# see https://wordpress.org/plugins/klubraum-membership-request/
		# special token can be created in app
		# https://api.klubraum.com/api-v1/user/membershipRequest/public
		headers = {"X-Api-Version": self.api_version, "X-Auth-Token": token, "Content-Type": "application/json"}
		url = "%s/user/membershipRequest/public" % self.base_url
		data = {
			"loginId": email
		}
		r = requests.post(url, json=data, headers=headers)
		self.__check_status_code(r)
		return r.json()["success"]

	def batch_invite(self, tenant_id, emails, language="de"):
		# does a batch invite with list of emails for club with tenant_id
		# requires admin login auth token
		# /api-v1/user/batchInvite?tenantId=851d7b1e-d5cd-4e30-a5db-611fb620dce4
		assert self.login_done
		assert tenant_id in self.tenants
		assert tenant_id in self.memberships
		assert "Administrator" in self.user_memberships[tenant_id]
		headers = {"X-Api-Version": self.api_version, "X-Auth-Token": self.auth_token, "Content-Type": "application/json"}
		url = "%s/user/batchInvite?tenantId=%s" % (self.base_url, tenant_id)
		data = {
			"loginIds": emails,
			"language": language,
		}

		# need to parse chunked response
		r = requests.post(url, json=data, headers=headers, stream=True)
		self.__check_status_code(r)

		# parse chunked response
		r_data = b""
		for line in r.iter_lines():
			# filter out keep-alive new lines
			if line:
				r_data += line

		# return value seem to have no newlines between single chunks. Need to split manually
		# return data is in format:
		# { "l": "email1@foo.com", "s": 1 }{ "l": "email1@bar.com", "s": 1 }
		# with no brakes between chunks

		r_data = r_data.decode("utf-8")
		r_data = r_data.replace("}{", "},{")
		r_data = "[%s]" % r_data
		j = json.loads(r_data)
		# return a dict with email as key and status as value
		return j

	def logout(self):
		self.auth_token = None
		self.login_done = False
		self.user_summary = None
