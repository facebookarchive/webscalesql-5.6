# Copyright (c) 2009, 2013, Oracle and/or its affiliates. All rights reserved.
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA 

MACRO (MYSQL_USE_BUNDLED_ZLIB)
  SET(ZLIB_LIBRARY zlib CACHE INTERNAL "Bundled zlib library")
  SET(ZLIB_INCLUDE_DIR  ${CMAKE_SOURCE_DIR}/zlib)
  SET(ZLIB_FOUND  TRUE)
  SET(WITH_ZLIB "bundled" CACHE STRING "Use bundled zlib")
  ADD_SUBDIRECTORY(zlib)
  GET_TARGET_PROPERTY(src zlib SOURCES)
  FOREACH(file ${src})
    SET(ZLIB_SOURCES ${ZLIB_SOURCES} ${CMAKE_SOURCE_DIR}/zlib/${file})
  ENDFOREACH()
ENDMACRO()

# MYSQL_CHECK_ZLIB_WITH_COMPRESS
#
# Provides the following configure options:
# WITH_ZLIB_BUNDLED
# If this is set,we use bindled zlib
# If this is not set,search for system zlib. 
# if system zlib is not found, use bundled copy
# ZLIB_LIBRARIES, ZLIB_INCLUDE_DIR and ZLIB_SOURCES
# are set after this macro has run

MACRO (MYSQL_CHECK_ZLIB_WITH_COMPRESS)

  IF(CMAKE_SYSTEM_NAME STREQUAL "OS400" OR 
     CMAKE_SYSTEM_NAME STREQUAL "AIX" OR
     CMAKE_SYSTEM_NAME STREQUAL "Windows")
    # Use bundled zlib on some platforms by default (system one is too
    # old or not existent)
    IF (NOT WITH_ZLIB)
      SET(WITH_ZLIB "bundled"  CACHE STRING "By default use bundled zlib on this platform")
    ENDIF()
  ENDIF()
  
  # See if WITH_ZLIB is of the form </path/to/custom/installation>
  FILE(GLOB WITH_ZLIB_HEADER ${WITH_ZLIB}/include/zlib.h)
  IF (WITH_ZLIB_HEADER)
    SET(WITH_ZLIB_PATH ${WITH_ZLIB} CACHE PATH "path to custom ZLIB installation")
  ENDIF()

  IF(WITH_ZLIB STREQUAL "bundled")
    MYSQL_USE_BUNDLED_ZLIB()
  ELSEIF(WITH_ZLIB STREQUAL "system" OR
         WITH_ZLIB STREQUAL "yes" OR
         WITH_ZLIB_PATH)
    # First search in WITH_SSL_PATH.
    FIND_PATH(ZLIB_ROOT_DIR
      NAMES include/zlib.h
      NO_CMAKE_PATH
      NO_CMAKE_ENVIRONMENT_PATH
      HINTS ${WITH_ZLIB_PATH}
    )
    # Then search in standard places (if not found above).
    FIND_PATH(ZLIB_ROOT_DIR
      NAMES include/zlib.h
    )

    IF(ZLIB_ROOT_DIR)
      INCLUDE(CheckFunctionExists)
      SET(CMAKE_REQUIRED_LIBRARIES z)
      CHECK_FUNCTION_EXISTS(crc32 HAVE_CRC32)
      CHECK_FUNCTION_EXISTS(compressBound HAVE_COMPRESSBOUND)
      CHECK_FUNCTION_EXISTS(deflateBound HAVE_DEFLATEBOUND)
      SET(CMAKE_REQUIRED_LIBRARIES)
      IF(HAVE_CRC32 AND HAVE_COMPRESSBOUND AND HAVE_DEFLATEBOUND)
        SET(ZLIB_LIBRARY "${ZLIB_ROOT_DIR}/lib/libz.so")
        SET(ZLIB_INCLUDE_DIR "${ZLIB_ROOT_DIR}/include")
        FILE(READ "${ZLIB_INCLUDE_DIR}/zlib.h" ZLIB_H)
        STRING(REGEX REPLACE ".*#define ZLIB_VERSION \"([0-9]+)\\.([0-9]+)\\.([0-9]+)\".*" "\\1.\\2.\\3" ZLIB_VERSION_STRING "${ZLIB_H}")
        SET(ZLIB_INCLUDE_DIRS ${ZLIB_INCLUDE_DIR})
        SET(ZLIB_FOUND TRUE CACHE INTERNAL "Zlib found")
        IF(WITH_ZLIB_PATH)
          SET(WITH_ZLIB "${WITH_ZLIB_PATH}" CACHE STRING "Using a custom zlib path")
        ELSE()
          SET(WITH_ZLIB "system" CACHE STRING
              "Which zlib to use (possible values are 'bundled' or 'system')")
        ENDIF()
        SET(ZLIB_SOURCES "")
      ELSE()
        SET(ZLIB_FOUND FALSE CACHE INTERNAL "Zlib found but not usable")
        MESSAGE(SEND_ERROR "system zlib found but not usable")
      ENDIF()
    ENDIF()
    IF(NOT ZLIB_FOUND)
      MYSQL_USE_BUNDLED_ZLIB()
    ENDIF()
  ENDIF()
  SET(HAVE_COMPRESS 1)
ENDMACRO()
