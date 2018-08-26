#!/usr/bin/env python
# -*- coding: utf-8 -*-

#-----------------------------------
# AutoNaptPython 
#
# Copyright (c) 2018 RainForest
#
# This software is released under the MIT License.
# http://opensource.org/licenses/mit-license.php
#-----------------------------------

import os
import sys
import select
import threading
import time
import configparser

from threading import Lock
from Utils import Utils
from datetime import datetime as dt

from elasticsearch import Elasticsearch

class ElasticConnector(object):
    def __init__(self):
        ini_file = os.path.join( os.path.dirname( os.path.abspath( __file__ ) ), '../elastic.ini')

        config = configparser.ConfigParser()
        config.read( ini_file )

        conf_url          = config.get('env', 'url')
        conf_verify_certs = False if config.get('env', 'verify_certs').lower() == "false" else True

        self.es = Elasticsearch(conf_url, verify_certs=False)
        self.settings = {
            "settings": {
              "index": {
                "creation_date": "1533116700171",
                "number_of_shards": "5",
                "number_of_replicas": "1",
                "uuid": "3sQuMexES4WE8D5f89INFA",
                "version": {
                  "created": "6020399"
                },
                "provided_name": "autonapt"
              }
            }
        }
        self.mapping = {
          "log": {
            "properties": {
              "client": {
                "properties": {
                  "local": {
                    "properties": {
                      "address": {
                        "type": "ip",
                        "fields": {
                          "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                          }
                        }
                      },
                      "port": {
                        "type": "long"
                      }
                    }
                  },
                  "remote": {
                    "properties": {
                      "address": {
                        "type": "ip",
                        "fields": {
                          "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                          }
                        }
                      },
                      "geoip": {
                        "properties": {
                          "asn": {
                            "properties": {
                              "asn": {
                                "type": "text",
                                "fields": {
                                  "keyword": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                  }
                                }
                              }
                            }
                          },
                          "city": {
                            "properties": {
                              "divisions": {
                                "type": "text",
                                "fields": {
                                  "keyword": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                  }
                                }
                              },
                              "iso_code": {
                                "type": "text",
                                "fields": {
                                  "keyword": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                  }
                                }
                              },
                              "location": {
                                "type": "geo_point"
                              },
                              "name": {
                                "type": "text",
                                "fields": {
                                  "keyword": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                  }
                                }
                              },
                              "postal_code": {
                                "type": "text",
                                "fields": {
                                  "keyword": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                  }
                                }
                              }
                            }
                          }
                        }
                      },
                      "port": {
                        "type": "long"
                      }
                    }
                  }
                }
              },
              "connection_id": {
                "type": "long"
              },
              "datetime": {
                "type": "date",
                "fields": {
                  "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                  }
                }
              },
              "protocol": {
                "type": "text",
                "fields": {
                  "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                  }
                }
              },
              "server": {
                "properties": {
                  "local": {
                    "properties": {
                      "address": {
                        "type": "text",
                        "fields": {
                          "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                          }
                        }
                      },
                      "port": {
                        "type": "long"
                      }
                    }
                  },
                  "remote": {
                    "properties": {
                      "address": {
                        "type": "text",
                        "fields": {
                          "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                          }
                        }
                      },
                      "port": {
                        "type": "long"
                      }
                    }
                  }
                }
              },
              "type": {
                "type": "text",
                "fields": {
                  "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                  }
                }
              }
            }
          }
        }

    def create(self, index_name):
        if self.es.indices.exists(index=index_name):
            return

        #self.es.indices.create(index=index_name, body=self.settings)
        self.es.indices.create(index=index_name)
        self.es.indices.put_mapping(index=index_name, doc_type='log', body=self.mapping)

    def store(self, datas):
        tdatetime = dt.now()
        index_name = "autonapt-%s" % (tdatetime.strftime('%Y%m%d'))
        self.create( index_name )

        # 2018-08-01 09:49:53.571078
        tstr = datas['datetime']
        datas['datetime'] = dt.strptime(tstr, '%Y-%m-%d %H:%M:%S.%f')

        return self.es.index(index=index_name, doc_type="log", body=datas)

    def search(self, datas):
        return self.es.search(index="autonapt-*", body=datas)

    def delete(self):
        return self.es.indices.delete(index="autonapt-*")

if __name__ == '__main__':
    obj = ElasticConnector()
    #tdatetime = dt.now()
    #index_name = "autonapt-%s" % (tdatetime.strftime('%Y%m%d'))
    #obj.delete( )

#    print obj.delete( )
#    print obj.create( )
#    print obj.es
#    print obj.store( {"name":"apple", "color":"green"} )
#    print obj.search( {"query": {"match_all": {}}} )

