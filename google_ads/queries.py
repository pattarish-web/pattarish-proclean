"""GAQL queries for full HFT export. Use {date_clause} placeholder."""

from __future__ import annotations

# Lifetime / structure (no date segment)
CAMPAIGN_SETTINGS = """
    SELECT
      campaign.id,
      campaign.name,
      campaign.status,
      campaign.advertising_channel_type,
      campaign.bidding_strategy_type,
      campaign.start_date,
      campaign.end_date,
      campaign_budget.amount_micros,
      campaign_budget.name
    FROM campaign
    WHERE campaign.status != 'REMOVED'
    ORDER BY campaign.name
"""

AD_GROUP_SETTINGS = """
    SELECT
      campaign.id,
      campaign.name,
      ad_group.id,
      ad_group.name,
      ad_group.status,
      ad_group.type
    FROM ad_group
    WHERE ad_group.status != 'REMOVED'
    ORDER BY campaign.name, ad_group.name
"""

# Performance with date range
CAMPAIGNS_DAILY = """
    SELECT
      campaign.id,
      campaign.name,
      campaign.status,
      segments.date,
      metrics.impressions,
      metrics.clicks,
      metrics.ctr,
      metrics.average_cpc,
      metrics.cost_micros,
      metrics.conversions,
      metrics.conversions_value,
      metrics.cost_per_conversion
    FROM campaign
    WHERE segments.date {date_clause}
      AND campaign.status != 'REMOVED'
    ORDER BY segments.date DESC
"""

AD_GROUPS_DAILY = """
    SELECT
      campaign.name,
      ad_group.id,
      ad_group.name,
      segments.date,
      metrics.impressions,
      metrics.clicks,
      metrics.ctr,
      metrics.average_cpc,
      metrics.cost_micros,
      metrics.conversions,
      metrics.cost_per_conversion
    FROM ad_group
    WHERE segments.date {date_clause}
      AND ad_group.status != 'REMOVED'
"""

KEYWORDS = """
    SELECT
      campaign.name,
      ad_group.name,
      ad_group_criterion.criterion_id,
      ad_group_criterion.keyword.text,
      ad_group_criterion.keyword.match_type,
      ad_group_criterion.status,
      ad_group_criterion.quality_info.quality_score,
      metrics.impressions,
      metrics.clicks,
      metrics.ctr,
      metrics.average_cpc,
      metrics.cost_micros,
      metrics.conversions,
      metrics.cost_per_conversion
    FROM keyword_view
    WHERE segments.date {date_clause}
      AND ad_group_criterion.status != 'REMOVED'
    ORDER BY metrics.cost_micros DESC
"""

SEARCH_TERMS = """
    SELECT
      campaign.name,
      ad_group.name,
      search_term_view.search_term,
      search_term_view.status,
      metrics.impressions,
      metrics.clicks,
      metrics.ctr,
      metrics.average_cpc,
      metrics.cost_micros,
      metrics.conversions,
      metrics.cost_per_conversion
    FROM search_term_view
    WHERE segments.date {date_clause}
    ORDER BY metrics.impressions DESC
"""

ADS = """
    SELECT
      campaign.name,
      ad_group.name,
      ad_group_ad.ad.id,
      ad_group_ad.ad.type,
      ad_group_ad.ad.final_urls,
      ad_group_ad.ad.responsive_search_ad.headlines,
      ad_group_ad.ad.responsive_search_ad.descriptions,
      ad_group_ad.status,
      metrics.impressions,
      metrics.clicks,
      metrics.ctr,
      metrics.average_cpc,
      metrics.cost_micros,
      metrics.conversions
    FROM ad_group_ad
    WHERE segments.date {date_clause}
      AND ad_group_ad.status != 'REMOVED'
"""

NEGATIVE_KEYWORDS = """
    SELECT
      campaign.name,
      ad_group.name,
      campaign_criterion.keyword.text,
      campaign_criterion.keyword.match_type,
      campaign_criterion.negative
    FROM campaign_criterion
    WHERE campaign_criterion.type = 'KEYWORD'
      AND campaign_criterion.negative = TRUE
"""

CONVERSION_ACTIONS = """
    SELECT
      conversion_action.id,
      conversion_action.name,
      conversion_action.status,
      conversion_action.type,
      conversion_action.category,
      conversion_action.origin
    FROM conversion_action
    WHERE conversion_action.status != 'REMOVED'
"""

QUERY_TEMPLATES = {
    "01_campaign_settings": CAMPAIGN_SETTINGS,
    "02_ad_group_settings": AD_GROUP_SETTINGS,
    "03_campaigns_daily": CAMPAIGNS_DAILY,
    "04_ad_groups_daily": AD_GROUPS_DAILY,
    "05_keywords": KEYWORDS,
    "06_search_terms": SEARCH_TERMS,
    "07_ads": ADS,
    "08_negative_keywords_campaign": NEGATIVE_KEYWORDS,
    "09_conversion_actions": CONVERSION_ACTIONS,
}


def build_queries(date_clause: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for name, template in QUERY_TEMPLATES.items():
        if "{date_clause}" in template:
            out[name] = template.format(date_clause=date_clause)
        else:
            out[name] = template
    return out
