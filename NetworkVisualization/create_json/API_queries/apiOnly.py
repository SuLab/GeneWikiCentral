

from wikidataintegrator import wdi_core, wdi_login, wdi_helpers, wdi_settings

username = wdi_settings.getWikiDataUser()
password = wdi_settings.getWikiDataPassword()
login_instance = wdi_login.WDLogin(user=username, pwd=password)

wdi_core.WDItemEngine(wd_item_id='Q414043|Q17910011')

test=wdi_core.WDItemEngine(wd_item_id='Q414043')
>>> test.get_property_list()


my_first_wikidata_item.get_wd_json_representation()
