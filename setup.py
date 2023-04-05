#!/usr/bin/env python
# -*- coding: utf8 -*-
# library for communicating with an isc dhcp server over the omapi protocol
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import distutils.core

distutils.core.setup(name='klubraum_api',
	version='0.1',
	description="Klubraum API implementation for Python",
	long_description="This module provides some functions for club management app Klubraum (https://klubraum.com) API",
	author='Torge Valerius',
	author_email='torge+github@valerius.email',
	license='Apache-2.0',
	url='https://github.com/cygnusb/klubraum_api',
	py_modules=['klubraum_api'],
	classifiers=[
		"Development Status :: 4 - Beta",
		"Intended Audience :: Other Audience",
		"License :: OSI Approved :: Apache Software License",
		"Programming Language :: Python",
		"Programming Language :: Python :: 3",
		"Programming Language :: Python :: 3.7",
		"Programming Language :: Python :: 3.8",
		"Topic :: Internet",
		"Topic :: System :: Networking",
		"Topic :: Software Development :: Libraries :: Python Modules",
	]
)
