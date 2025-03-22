
SELECT * 
	FROM IDM.DW_IDM_GROUP dig
	WHERE GROUP_NAME IN ( '@Digital Cloud Services Team'
		, '@GE AWS_acct-admin_736489861251'
		, '@GE AWS_bu-corp-brt-cc_736489861251'
		, '@GE AWS_bu-corp-brt-ro_736489861251'
		, '@GE AWS_bu-ge-cirt-cc_556003251088'
		, '@GE AWS_bu-ge-cirt-ro_556003251088'
		, '@GE AWS_bu-iam-admin_188894168332'
		, '@GE AWS_bu-iam-admin_207755114178'
		, '@GE AWS_bu-iam-admin_264560008398'
		, '@GE AWS_bu-iam-admin_504948279284'
		, '@GE AWS_bu-iam-admin_556003251088'
		, '@GE AWS_bu-iam-admin_736489861251'
		, '@GE AWS_bu-iam-admin_908835901277'
		, '@GE AWS_bu-terraformer_264560008398'
		, '@GE AWS_bu-terraformer_556003251088'
		, '@GE AWS_cct-CorporateDBA_207755114178'
		, '@GE AWS_corp-bu-waf-manager_736489861251'
		, '@GE AWS_corp-network-firewall-manager_736489861251'
		, '@GE AWS_cs/p-jump-av-fw-cirt_589623221417'
		, '@GE AWS_cs/p-jump-billing_589623221417'
		, '@GE AWS_cs/p-jump-cloud-delivery_589623221417'
		, '@GE AWS_cs/p-jump-cloud-platforms_589623221417'
		, '@GE AWS_cs/p-jump-cloud-services_589623221417'
		, '@GE AWS_cs/p-jump-engineering_589623221417'
		, '@GE AWS_cs/p-jump-hosting-billing-admins_589623221417'
		, '@GE AWS_cs/p-jump-master-payers_589623221417'
		, '@GE AWS_cs/p-jump-network-engineers_589623221417'
		, '@GE AWS_cs/p-jump-organizations-admins_589623221417'
		, '@GE AWS_cs/p-jump-organizations-users_589623221417'
		, '@GE AWS_cs/p-jump-platformadmins_589623221417'
		, '@GE AWS_cs/p-jump-support_589623221417'
		, '@GE AWS_dbss/p-jump-db-devops_589623221417'
		, '@GE AWS_dbss/p-jump-dba_589623221417'
		, '@GE AWS_enterprise-billing-user_737859062117'
		, '@GE AWS_mc-m-dba_207755114178'
		, '@GE AWS_mc/m-jump-dba_589623221417'
		, '@GE Cloud Hosting - Cloud Delivery'
		, '@GE Cloud Hosting - DL Approvers'
		, '@GE Cloud Hosting - GESOS'
		, '@GE GOVAWS_bu-ge-cirt-cc_147947222044'
		, '@GE GOVAWS_bu-ge-cirt-ro_147947222044'
		, '@GE GOVAWS_bu-poweruser_147947222044'
		, '@GE GOVAWS_bu-poweruser_330271845325'
		, '@GE GOVAWS_bu-terraformer_147947222044'
		, '@GE GOVAWS_bu-terraformer_715477192348'
		, '@GE GOVAWS_cs/bu-iam-admin_147947222044'
		, '@GE GOVAWS_cs/bu-iam-admin_330271845325'
		, '@GE GOVAWS_cs/ge-cirt-auto_147947222044'
		, '@GE GOVAWS_cs/ge-cirt-cc_147947222044'
		, '@GE GOVAWS_cs/ge-cirt-ro_147947222044'
		, '@GE GOVAWS_cs/p-jump-cloud-delivery_020202940623'
		, '@GE GOVAWS_cs/p-jump-cloud-services_020202940623'
		, '@GE GOVAWS_cs/p-jump-engineering_020202940623'
		, '@GE GOVAWS_cs/p-jump-network-engineers_020202940623'
		, '@GE GOVAWS_cs/p-jump-organizations-admins_020202940623'
		, '@GE GOVAWS_cs/p-jump-organizations-users_020202940623'
		, '@GE GOVAWS_cs/p-jump-support_020202940623'
	)
ORDER BY GROUP_NAME 

SELECT dig.GROUP_ID
	, dig.LDAP_HOST
	, dig.LDAP_OU
	, dig.GROUP_NAME
	, dig.ATTR_GECPASECURITYGROUP
	, dig.PRIMARY_MANAGER_SSO
	, TRIM (',' FROM iu.FIRST_NAME || ' ' || iu.MIDDLE_NAME  || ', ' || iu.LAST_NAME) AS FULL_NAME
	, iu.EMAIL_DISPLAY_NAME
    , iu.EMAIL_ADDRESS 
    , iu.PERSON_STATUS
    , iu.PERSON_TYPE
    , iu.USER_ID
    , iu.JOB_TITLE
    , iu.JOB_FUNCTION
    , iu.SSO_EXPIRATION_DATE
    , iu.LAST_UPDATE_DATE
    , iu.EFFECTIVE_DATE
    , iu.INDUSTRY_FOCUS_NAME
    , iu.BUSINESS_SEGMENT
    , iu.COMPANYNAME
    , iu.DEPARTMENT_NAME
    FROM IDM.DW_IDM_GROUP dig 
JOIN IDM.IDM_USER iu ON dig.PRIMARY_MANAGER_SSO = iu.PERSON_NUM_SSO	
	WHERE dig.GROUP_NAME IN ( '@Digital Cloud Services Team'
		, '@GE AWS_acct-admin_736489861251'
		, '@GE AWS_bu-corp-brt-cc_736489861251'
		, '@GE AWS_bu-corp-brt-ro_736489861251'
		, '@GE AWS_bu-ge-cirt-cc_556003251088'
		, '@GE AWS_bu-ge-cirt-ro_556003251088'
		, '@GE AWS_bu-iam-admin_188894168332'
		, '@GE AWS_bu-iam-admin_207755114178'
		, '@GE AWS_bu-iam-admin_264560008398'
		, '@GE AWS_bu-iam-admin_504948279284'
		, '@GE AWS_bu-iam-admin_556003251088'
		, '@GE AWS_bu-iam-admin_736489861251'
		, '@GE AWS_bu-iam-admin_908835901277'
		, '@GE AWS_bu-terraformer_264560008398'
		, '@GE AWS_bu-terraformer_556003251088'
		, '@GE AWS_cct-CorporateDBA_207755114178'
		, '@GE AWS_corp-bu-waf-manager_736489861251'
		, '@GE AWS_corp-network-firewall-manager_736489861251'
		, '@GE AWS_cs/p-jump-av-fw-cirt_589623221417'
		, '@GE AWS_cs/p-jump-billing_589623221417'
		, '@GE AWS_cs/p-jump-cloud-delivery_589623221417'
		, '@GE AWS_cs/p-jump-cloud-platforms_589623221417'
		, '@GE AWS_cs/p-jump-cloud-services_589623221417'
		, '@GE AWS_cs/p-jump-engineering_589623221417'
		, '@GE AWS_cs/p-jump-hosting-billing-admins_589623221417'
		, '@GE AWS_cs/p-jump-master-payers_589623221417'
		, '@GE AWS_cs/p-jump-network-engineers_589623221417'
		, '@GE AWS_cs/p-jump-organizations-admins_589623221417'
		, '@GE AWS_cs/p-jump-organizations-users_589623221417'
		, '@GE AWS_cs/p-jump-platformadmins_589623221417'
		, '@GE AWS_cs/p-jump-support_589623221417'
		, '@GE AWS_dbss/p-jump-db-devops_589623221417'
		, '@GE AWS_dbss/p-jump-dba_589623221417'
		, '@GE AWS_enterprise-billing-user_737859062117'
		, '@GE AWS_mc-m-dba_207755114178'
		, '@GE AWS_mc/m-jump-dba_589623221417'
		, '@GE Cloud Hosting - Cloud Delivery'
		, '@GE Cloud Hosting - DL Approvers'
		, '@GE Cloud Hosting - GESOS'
		, '@GE GOVAWS_bu-ge-cirt-cc_147947222044'
		, '@GE GOVAWS_bu-ge-cirt-ro_147947222044'
		, '@GE GOVAWS_bu-poweruser_147947222044'
		, '@GE GOVAWS_bu-poweruser_330271845325'
		, '@GE GOVAWS_bu-terraformer_147947222044'
		, '@GE GOVAWS_bu-terraformer_715477192348'
		, '@GE GOVAWS_cs/bu-iam-admin_147947222044'
		, '@GE GOVAWS_cs/bu-iam-admin_330271845325'
		, '@GE GOVAWS_cs/ge-cirt-auto_147947222044'
		, '@GE GOVAWS_cs/ge-cirt-cc_147947222044'
		, '@GE GOVAWS_cs/ge-cirt-ro_147947222044'
		, '@GE GOVAWS_cs/p-jump-cloud-delivery_020202940623'
		, '@GE GOVAWS_cs/p-jump-cloud-services_020202940623'
		, '@GE GOVAWS_cs/p-jump-engineering_020202940623'
		, '@GE GOVAWS_cs/p-jump-network-engineers_020202940623'
		, '@GE GOVAWS_cs/p-jump-organizations-admins_020202940623'
		, '@GE GOVAWS_cs/p-jump-organizations-users_020202940623'
		, '@GE GOVAWS_cs/p-jump-support_020202940623'
	)
	ORDER BY dig.GROUP_NAME ASC, dig.GROUP_ID ASC
