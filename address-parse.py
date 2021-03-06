import os
import json
import pprint

from smartystreets_python_sdk import StaticCredentials, exceptions, ClientBuilder
from smartystreets_python_sdk.us_street import Lookup


def run():
	auth_id = '1d3ba9eb-6df4-74ec-fa31-d23fe2d89162'
	auth_token = '5RqNDBSfOAq3jdN7OgMc'

	# We recommend storing your secret keys in environment variables instead---it's safer!
	# auth_id = os.environ['SMARTY_AUTH_ID']
	# auth_token = os.environ['SMARTY_AUTH_TOKEN']

	credentials = StaticCredentials(auth_id, auth_token)

	client = ClientBuilder(credentials).build_us_street_api_client()
	# client = ClientBuilder(credentials).with_proxy('localhost:8080', 'user', 'password').build_us_street_api_client()
	# Uncomment the line above to try it with a proxy instead

	address = '350 S Main, Salt Lake City, UT, 84101'
	lookup = Lookup(address)
	#lookup.street = "1600 Amphitheatre Pkwy"
	#lookup.city = "Mountain View"
	#lookup.state = "CA"
	#lookup.street = 'Union Station, 1717 Pacific Ave, #2100, Tacoma, WA 98402'

	try:
		client.send_lookup(lookup)
	except exceptions.SmartyException as err:
		print(err)
		return

	result = lookup.result

	if not result:
		print("No candidates. This means the address is not valid.")
		return

	first_candidate = result[0]

	print("Address is valid. (There is at least one candidate)\n")
	print("ZIP Code: " + first_candidate.components.zipcode)
	print("County: " + first_candidate.metadata.county_name)
	print("Latitude: {}".format(first_candidate.metadata.latitude))
	print("Longitude: {}".format(first_candidate.metadata.longitude))


if __name__ == "__main__":
	run()


