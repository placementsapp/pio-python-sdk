"""
Models for the GET API Endpoints
"""

from typing import TypedDict
from datetime import datetime


class ModelFilterDefaults(TypedDict):
    """
    Default API Filters that exist for all services
    """

    id: int
    modified_since: datetime
    name: str
    uid: str


class ModelFilterAccount(ModelFilterDefaults):
    """
    API Filters for Accounts
    """

    account_type: str
    external_id: str
    archived: bool
    advertiser_of_record: int
    agency_of_record: int


class ModelFilterCampaign(ModelFilterDefaults):
    """
    API Filters for Campaigns
    """

    ad_server_network_code: int
    ad_server_id: int
    archived: bool
    campaign_number: int


class ModelFilterContact(ModelFilterDefaults):
    """
    API Filters for Contacts
    """


class ModelFilterCreative(ModelFilterDefaults):
    """
    API Filters for Creatives
    """


class ModelFilterCustomField(ModelFilterDefaults):
    """
    API Filters for Custom Fields
    """


class ModelFilterGroup(ModelFilterDefaults):
    """
    API Filters for Groups
    """

    ad_server_network_code: int
    ad_server_id: int
    campagign: int


class ModelFilterLineItem(ModelFilterDefaults):
    """
    API Filters for Line Items
    """

    ad_server_network_code: int
    archived: bool
    approval_status: str
    delivery_status: str
    started_before: datetime
    started_after: datetime
    ended_before: datetime
    ended_after: datetime
    ad_server_id: int
    campaign: int
    group: int


class ModelFilterOpportunity(ModelFilterDefaults):
    """
    API Filters for Opportunities
    """

    archived: bool
    opportunity_order_number: int


class ModelFilterOpportunityLineItem(ModelFilterDefaults):
    """
    API Filters for Opportunity Line Items
    """

    ad_server_network_code: int
    archived: bool
    started_before: datetime
    started_after: datetime
    ended_before: datetime
    ended_after: datetime
    opportunity: int


class ModelFilterPackage(ModelFilterDefaults):
    """
    API Filters for Packages
    """

    active: bool
    archived: bool


class ModelFilterProduct(ModelFilterDefaults):
    """
    API Filters for Products
    """

    ad_server: str
    ad_server_network_code: int
    active: bool
    archived: bool


class ModelFilterProductRate(ModelFilterDefaults):
    """
    API Filters for Product Rates
    """


class ModelFilterRateCard(ModelFilterDefaults):
    """
    API Filters for Rate Cards
    """


class ModelFilterReport(ModelFilterDefaults):
    """
    API Filters for Reports
    """


class ModelFilterUser(ModelFilterDefaults):
    """
    API Filters for Users
    """

    email: str
