from typing import TypedDict, Unpack
from datetime import datetime


class ModelFilterDefaults(TypedDict):
    id: int
    modified_since: datetime
    name: str
    uid: str
    org_id: int


class ModelFilterAccount(ModelFilterDefaults):
    account_type: str
    external_id: str
    archived: bool
    advertiser_of_record: int
    agency_of_record: int


class ModelFilterCampaign(ModelFilterDefaults):
    ad_server_network_code: int
    ad_server_id: int
    archived: bool
    campaign_number: int


class ModelFilterContact(ModelFilterDefaults):
    pass


class ModelFilterCreative(ModelFilterDefaults):
    pass


class ModelFilterCustomField(ModelFilterDefaults):
    pass


class ModelFilterGroup(ModelFilterDefaults):
    ad_server_network_code: int
    ad_server_id: int
    campagign: int


class ModelFilterLineItem(ModelFilterDefaults):
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
    archived: bool
    opportunity_order_number: int


class ModelFilterOpportunityLineItem(ModelFilterDefaults):
    ad_server_network_code: int
    archived: bool
    started_before: datetime
    started_after: datetime
    ended_before: datetime
    ended_after: datetime
    opportunity: int


class ModelFilterPackage(ModelFilterDefaults):
    active: bool
    archived: bool


class ModelFilterProduct(ModelFilterDefaults):
    ad_server: str
    ad_server_network_code: int
    active: bool
    archived: bool


class ModelFilterProductRate(ModelFilterDefaults):
    pass


class ModelFilterRateCard(ModelFilterDefaults):
    pass


class ModelFilterReport(ModelFilterDefaults):
    pass


class ModelFilterUser(ModelFilterDefaults):
    email: str
