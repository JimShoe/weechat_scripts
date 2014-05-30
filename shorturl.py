#!/usr/bin/python
#
# Copyright (C) 2014 Nathan Warner <nathan@frcv.net>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#
# Colors and shotens urls inline.  Adds shorturl function to shorten
# and print url to current buffer.
#
# *NOTE*: Shorten urls may be printed after other lines depending on how long
#         it takes for the shortener to reply.
#
# History:
#
# 2014-02-19, Nathan Warner <nathan@frcv.net>:
#     v0.4: Fixed error with regex sub.
#         : Changed to usinig .format for strings.
# 2014-02-17, Nathan Warner <nathan@frcv.net>:
#     v0.3: Added v.gd and narro.ws as shorteners.
#         : Fixed issue with not coloring multiple urls.
#         : Added license.
# 2014-02-11, Nathan Warner <nathan@frcv.net>:
#     v0.2: Added url quoting before sending off.
# 2014-02-07, Nathan Warner <nathan@frcv.net>:
#     v0.1: Inital release.
#
# Help about settings:
#   display all settings for script (or use iset.pl script to change settings):
#      /set plugins.var.python.shorturl.*
#

import weechat
import re
import urllib

SCRIPT_NAME    = "shorturl"
SCRIPT_AUTHOR  = "JimShoe <nathan@frcv.net>"
SCRIPT_VERSION = "0.3"
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
  if shortener == 'rldn.net':
    status, url = out.split()
  if shortener == 'is.gd' or shortener == 'v.gd' or shortener == 'narro.ws':
    url = out
  color_url = "{color}{url}{reset}".format(color=color, url=url, reset=reset)
  weechat.prnt(data, color_url)
  return weechat.WEECHAT_RC_OK

# call hook_process based on shortener setting
def shorten(buffer, url):
  shortener = weechat.config_get_plugin('shortener')
  if shortener == 'rldn.net':
    url = "url:http://rldn.net/api/{url}".format(url=url)
  if shortener == 'is.gd':
    url = "url:http://is.gd/create.php?format=simple&url={url}".format(url=url)
  if shortener == 'v.gd':
    url = "url:http://v.gd/create.php?format=simple&url={url}".format(url=url)
  if shortener == 'narro.ws':
      url = "url:http://narro.ws/create/{url}".format(url=url)
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
  if weechat.info_get('irc_is_channel', '{moddata},{channel}'.format(moddata=modifier_data, channel=msg['channel'])) == '1':
    name = msg['channel']
  else:
    name = msg['nick']
  buffer_full_name = '{moddata}.{name}'.format(moddata=modifier_data, name=name)
  return weechat.buffer_search("irc", buffer_full_name)

# Look for urls, color if too short, shorten if too long
def modifier_cb(data, modifier, modifier_data, string):
  urls = re.findall('[a-z]{2,5}://[^\s()\[\]]*', string)
  for url in urls:
    color = weechat.color(weechat.config_get_plugin("color"))
    reset = weechat.color('reset')
    urllength = int(weechat.config_get_plugin('urllength'))
    if len(url) < urllength:
      color_url = "{color}{url}{reset}".format(color=color, url=url, reset=reset)
      string = re.sub(re.escape(url), color_url, string)
    else:
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


