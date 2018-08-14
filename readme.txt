{
  "autonapt": {
    "aliases": {},
    "mappings": {
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
    },
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
}
