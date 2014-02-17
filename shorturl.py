#!/usr/bin/python
import weechat
import re
import urllib

SCRIPT_NAME    = "shorturl"
SCRIPT_AUTHOR  = "JimShoe <nathan@frcv.net>"
SCRIPT_VERSION = "0.1"
SCRIPT_LICENSE = "GPL3"
SCRIPT_DESC    = "Shortens url and puts them inline."

def end_script():
  return weechat.WEECHAT_RC_OK;

# Calback from hook_process in shorten
def print_short(data, command, rc, out, err):
  # bail if there is an error
  if rc != 0:
    return weechat.WEECHAT_RC_OK
  color = weechat.color(weechat.config_get_plugin("color"))
  reset = weechat.color('reset')
  shortener = weechat.config_get_plugin('shortener')
  # parse response based on shortener setting
  if shortener == 'rldn':
    status, url = out.split()
  if shortener == 'is.gd' or shortener == 'v.gd' or shortener == 'narro.ws':
    url = out
  weechat.prnt(data, '%(color)s%(url)s%(reset)s' % dict(color=color,reset=reset,url=url))
  return weechat.WEECHAT_RC_OK

# call hook_process based on shortener setting
def shorten(buffer, url):
  shortener = weechat.config_get_plugin('shortener')
  url = urllib.quote(url)
  if shortener == 'rldn':
    url = "url:http://rldn.net/api/%s" % (url,)
  if shortener == 'is.gd':
    url = "url:http://is.gd/create.php?format=simple&url=%s" % (url,)
  if shortener == 'v.gd':
    url = "url:http://v.gd/create.php?format=simple&url=%s" % (url,)
  if shortener == 'narro.ws':
      url = "url:http://narro.ws/create/%s" % (url,)
  weechat.hook_process(url,
    30 * 1000, 
    "print_short", 
    buffer) 
  return weechat.WEECHAT_RC_OK

# lets you shorten multiple urls by typing /shorten URL...
def shortenurl(data, buffer, args):
  if len(args) == 0:
    weechat.command("","/help shortenurl")
  urls = re.findall('[a-z]{2,5}://[^\s()\[\]]*', args)
  for url in urls:
    shorten(buffer, url)
  return weechat.WEECHAT_RC_OK

# returns buffer using data from hook_modifier
def getbuffer(modifier_data, string):
  msg = weechat.info_get_hashtable("irc_message_parse",{ "message": string })
  if weechat.info_get('irc_is_channel', '%s,%s' % (modifier_data, msg['channel'])) == '1':
    name = msg['channel']
  else:
    name = msg['nick']
  buffer_full_name = '%s.%s' % (modifier_data, name)
  return weechat.buffer_search("irc", buffer_full_name)

# Look for urls, color if too short, shorten if too long
def modifier_cb(data, modifier, modifier_data, string):
  urls = re.findall('[a-z]{2,5}://[^\s()\[\]]*', string)
  for url in urls:
    color = weechat.color(weechat.config_get_plugin("color"))
    reset = weechat.color('reset')
    urllength = int(weechat.config_get_plugin('urllength'))
    if len(url) < urllength:
      return re.sub(re.escape(url), "%(color)s%(url)s%(reset)s", string) % dict(color=color,reset=reset,url=url)
    buffer = getbuffer(modifier_data, string)
    shorten(buffer, url)
  return string

if __name__ == "__main__":
  if weechat.register(SCRIPT_NAME, SCRIPT_AUTHOR, SCRIPT_VERSION, SCRIPT_LICENSE, SCRIPT_DESC, "end_script", ""):
    weechat.hook_modifier("irc_in2_privmsg", "modifier_cb", "")
    weechat.hook_command("shortenurl", "Shortens a url and prints it to your current buffer.", "[<URL...>]", 
      "         URL: URL to shorten (multiple URLs may be given)\n", "", "shortenurl", "");

    settings = {
      'shortener': ('is.gd', 'URL Shortener to use. (is.gd, v.gd, rldn.net, narro.ws)'),
      'urllength': ('40', 'Max length of url before shortening.'),
      'color': ('lightblue', 'Color for all urls.'),
    }

    version = weechat.info_get('version_number', '')
    for option, default_desc in settings.iteritems():
      if not weechat.config_is_set_plugin(option):
        weechat.config_set_plugin(option, default_desc[0])
      if int(version) >= 0x00030500:
        weechat.config_set_desc_plugin(option, default_desc[1])


