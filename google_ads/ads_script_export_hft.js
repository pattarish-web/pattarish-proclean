/**
 * HFT Google Ads Export Script
 * ---------------------------------
 * How to use:
 * 1. Open Google Ads account HFT (359-752-1395)
 * 2. Tools > Scripts > + New script
 * 3. Paste this entire file
 * 4. Authorize when prompted
 * 5. Run main()
 * 6. Open the Google Sheet URL from Logs (Tools > Scripts > Logs)
 * 7. Download each sheet as CSV to your computer
 *
 * Optional: set SEND_EMAIL below to receive the sheet link by email.
 */

var CONFIG = {
  // Custom date range (YYYYMMDD). Change if needed.
  START_DATE: '20220101',
  END_DATE: '20260709',

  // Google Sheet title prefix
  SHEET_PREFIX: 'HFT_Ads_Export',

  // Set your email to receive the spreadsheet link (leave '' to skip)
  SEND_EMAIL: '',

  // Max rows per report (Google Ads Scripts limit ~200k per report)
  MAX_ROWS: 200000,
};

var DATE_RANGE = CONFIG.START_DATE + ',' + CONFIG.END_DATE;

function main() {
  var ss = SpreadsheetApp.create(CONFIG.SHEET_PREFIX + '_' + todayStr());
  var defaultSheet = ss.getSheets()[0];
  ss.deleteSheet(defaultSheet);
  Logger.log('Created spreadsheet: ' + ss.getUrl());

  exportReport(ss, '01_campaigns_daily', buildCampaignQuery());
  exportReport(ss, '02_ad_groups_daily', buildAdGroupQuery());
  exportReport(ss, '03_keywords', buildKeywordQuery());
  exportReport(ss, '04_search_terms', buildSearchTermsQuery());
  exportReport(ss, '05_ads', buildAdQuery());
  exportReport(ss, '06_campaign_settings', buildCampaignSettingsQuery());

  if (CONFIG.SEND_EMAIL) {
    MailApp.sendEmail(
      CONFIG.SEND_EMAIL,
      'HFT Google Ads Export ready',
      'Download CSV from each sheet:\n' + ss.getUrl()
    );
  }

  Logger.log('DONE. Open the spreadsheet URL above.');
  Logger.log('File > Download > Comma-separated values (.csv) per sheet tab.');
}

function todayStr() {
  return Utilities.formatDate(new Date(), 'Asia/Bangkok', 'yyyy-MM-dd_HHmm');
}

function exportReport(ss, sheetName, query) {
  Logger.log('Exporting: ' + sheetName);
  var sheet = ss.insertSheet(sheetName);
  var report = AdsApp.report(query);
  report.exportToSheet(sheet);
  Logger.log('  OK: ' + sheetName);
}

function buildCampaignQuery() {
  return (
    'SELECT CampaignId, CampaignName, CampaignStatus, AdvertisingChannelType, ' +
    'BiddingStrategyType, Date, Impressions, Clicks, Ctr, AverageCpc, Cost, ' +
    'Conversions, ConversionRate, CostPerConversion ' +
    'FROM CAMPAIGN_PERFORMANCE_REPORT ' +
  'WHERE Impressions >= 0 ' +
    'DURING ' + DATE_RANGE +
    ' ORDER BY Date DESC'
  );
}

function buildAdGroupQuery() {
  return (
    'SELECT CampaignName, AdGroupId, AdGroupName, AdGroupStatus, Date, ' +
    'Impressions, Clicks, Ctr, AverageCpc, Cost, Conversions, CostPerConversion ' +
    'FROM ADGROUP_PERFORMANCE_REPORT ' +
    'WHERE Impressions >= 0 ' +
    'DURING ' + DATE_RANGE +
    ' ORDER BY Cost DESC'
  );
}

function buildKeywordQuery() {
  return (
    'SELECT CampaignName, AdGroupName, Criteria, KeywordMatchType, QualityScore, ' +
    'Impressions, Clicks, Ctr, AverageCpc, Cost, Conversions, CostPerConversion ' +
    'FROM KEYWORDS_PERFORMANCE_REPORT ' +
    'WHERE Impressions >= 0 ' +
    'DURING ' + DATE_RANGE +
    ' ORDER BY Cost DESC'
  );
}

function buildSearchTermsQuery() {
  return (
    'SELECT CampaignName, AdGroupName, Query, QueryMatchTypeWithVariant, ' +
    'Impressions, Clicks, Ctr, AverageCpc, Cost, Conversions, CostPerConversion ' +
    'FROM SEARCH_QUERY_PERFORMANCE_REPORT ' +
    'WHERE Impressions > 0 ' +
    'DURING ' + DATE_RANGE +
    ' ORDER BY Impressions DESC'
  );
}

function buildAdQuery() {
  return (
    'SELECT CampaignName, AdGroupName, AdType, Id, ' +
    'Impressions, Clicks, Ctr, AverageCpc, Cost, Conversions ' +
    'FROM AD_PERFORMANCE_REPORT ' +
    'WHERE Impressions >= 0 ' +
    'DURING ' + DATE_RANGE +
    ' ORDER BY Impressions DESC'
  );
}

function buildCampaignSettingsQuery() {
  return (
    'SELECT CampaignId, CampaignName, CampaignStatus, AdvertisingChannelType, ' +
    'BiddingStrategyType, Amount, StartDate, EndDate ' +
    'FROM CAMPAIGN_PERFORMANCE_REPORT ' +
    'DURING ' + DATE_RANGE
  );
}
