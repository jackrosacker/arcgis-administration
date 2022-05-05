###############################################################################
# Script developed to fully compress the CPC eGDB 			      #
# References:                                    			      #
#	https://pro.arcgis.com/en/pro-app/2.8/help/data/geodatabases/overview/using-python-scripting-to-batch-reconcile-and-post-versions.htm
#	https://community.esri.com/t5/data-management-documents/compress-geodatabase-tool/ta-p/908944
# Collated by, on: JRosacker, 20220413			                      #
###############################################################################

# ToDos:
	# Todo: consider adding function to manage web services - pending initial test
	# Todo: add logging functions

# Import libraries
import arcpy
# import time	 # (required if user disconnect delay is activated)
# import smtplib # (required if email notifications are activated)

# Set the workspace 
arcpy.env.workspace = r"E:\ConnectionFiles\SDE@CPCOps.sde"

# Set a variable for the workspace
adminConn = arcpy.env.workspace

'''
def emailNotification():

	# Get a list of connected users.
	userList = arcpy.ListUsers(adminConn)

	# Get a list of user names of users currently connected and make email addresses
	emailList = [user.Name + "@yourcompany.com" for user in arcpy.ListUsers(adminConn)]

	# Take the email list and use it to send an email to connected users.
	SERVER = "mailserver.yourcompany.com"
	FROM = "SDE Admin <python@yourcompany.com>"
	TO = emailList
	SUBJECT = "Maintenance is about to be performed"
	MSG = "Auto generated Message.\n\rServer maintenance will be performed in 10 minutes. Please log off."

	# Prepare actual message
	MESSAGE = """\
	From: %s
	To: %s
	Subject: %s

	%s
	""" % (FROM, ", ".join(TO), SUBJECT, MSG)

	# Send the mail
	print("Sending email to connected users")
	server = smtplib.SMTP(SERVER)
	server.sendmail(FROM, TO, MESSAGE)
	server.quit()
'''

def blockConnections():

	# Block new connections to the database.
	print("The database is no longer accepting connections")
	arcpy.AcceptConnections(adminConn, False)

	# Wait 10 minutes (activate if notification is being sent to users)
	# time.sleep(600)

	# Disconnect all users from the database.
	print("Disconnecting all users")
	arcpy.DisconnectUser(adminConn, "ALL")

def reconcile():

	# Get a list of versions to pass into the ReconcileVersions tool.
	# Only reconcile versions that are children of Default.
	print("Compiling a list of versions to reconcile")
	verList = arcpy.da.ListVersions(adminConn)
	versionList = [ver.name for ver in verList if ver.parentVersionName == 'sde.DEFAULT']

	# Execute the ReconcileVersions tool.
	print("Reconciling all versions")
	arcpy.ReconcileVersions_management(
		adminConn					# Input database
		, "ALL_VERSIONS"				# Reconcile mode
		, "sde.DEFAULT"					# Target Version (optional)
		, versionList					# Edit versions (optional)
		, "LOCK_ACQUIRED"				# Acquire locks (optional)
		, "NO_ABORT"					# Abort if conflicts (optional)
		, "BY_OBJECT"					# Conflict definition (optional)
		, "FAVOR_TARGET_VERSION"		        # Conflict resolution (optional)
		, "POST"					# With post (optional)
		, "DELETE_VERSION"				# With delete (optional)
		#, "c:/temp/reconcilelog.txt"	                # Out log (optional)	
		)

def compress():
	
	# Run the compress tool. 
	print("Running compress")
	arcpy.Compress_management(adminConn)

def allowConnections():
	
	# Allow the database to begin accepting connections again.
	print("Allow users to connect to the database again")
	arcpy.AcceptConnections(adminConn, True)

def updateStatsAndIndexes():

	# Update statistics and indexes for the system tables.
	# Note: To use the "SYSTEM" option, the user must be an geodatabase or database administrator.
	# Rebuild indexes on the system tables.
	print("Rebuilding indexes on the system tables")
	arcpy.RebuildIndexes_management(adminConn, "SYSTEM")

	# Update statistics on the system tables.
	print("Updating statistics on the system tables")
	arcpy.AnalyzeDatasets_management(adminConn, "SYSTEM")

#emailNotification()
blockConnections()
reconcile()
compress()
allowConnections()
updateStatsAndIndexes()
