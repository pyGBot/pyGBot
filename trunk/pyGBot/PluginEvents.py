##
##    pyGBot - Versatile IRC Bot
##    Copyright (C) 2008 Morgan Lokhorst-Blight, Alex Soborov
##
##    This program is free software: you can redistribute it and/or modify
##    it under the terms of the GNU General Public License as published by
##    the Free Software Foundation, either version 3 of the License, or
##    (at your option) any later version.
##
##    This program is distributed in the hope that it will be useful,
##    but WITHOUT ANY WARRANTY; without even the implied warranty of
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##    GNU General Public License for more details.
##
##    You should have received a copy of the GNU General Public License
##    along with this program.  If not, see <http://www.gnu.org/licenses/>.
##

################################################################################
## 
## PluginEvents
## 
################################################################################

from contrib.Events import Events

class PluginEvents(Events):
    __events__ = ('user_join','user_part','user_kicked','user_quit','user_nickchange',
                  'bot_connect', 'bot_join', 'bot_kicked','bot_disconnect',
                  'msg_channel', 'msg_action', 'msg_private', 'msg_notice',
                  'channel_names', 'timer_tick')
