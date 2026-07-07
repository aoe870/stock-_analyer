# Miana API

**版本**: 1.0.0

Exported from DocumentExpand API definitions.

## 服务器地址

- http://124.222.142.232:9876

## 目录

- [api](#api)
  1. [GET 加密货币列表](#api-1)
  2. [GET 加密货币K线](#api-2)
  3. [GET 实时行情(返回整个市场实时行情)](#api-3)
  4. [GET 加密货币排序](#api-4)
  5. [GET 实时行情](#api-5)
  6. [GET 外汇列表](#api-6)
  7. [GET 外汇排行](#api-7)
  8. [GET 外汇K线](#api-8)
  9. [GET 外汇实时行情](#api-9)
  10. [GET 外汇实时行情(整个市场)](#api-10)
  11. [GET 基金资产配置](#api-11)
  12. [GET 基金列表](#api-12)
  13. [GET 实时行情(返回整个市场实时行情)](#api-13)
  14. [GET 基金排序(不包含货币基金和开放式基金)](#api-14)
  15. [GET 基金K线](#api-15)
  16. [GET 实时行情](#api-16)
  17. [GET 期货列表](#api-17)
  18. [GET 期货排行](#api-18)
  19. [GET 期货K线](#api-19)
  20. [GET 实时行情](#api-20)
  21. [GET 实时行情(返回整个市场实时行情)](#api-21)
  22. [GET 指数成分股列表](#api-22)
  23. [GET 指数列表](#api-23)
  24. [GET 实时行情(返回整个市场实时行情)](#api-24)
  25. [GET 指数排序](#api-25)
  26. [GET 指数K线](#api-26)
  27. [GET 实时行情](#api-27)
  28. [GET 贵金属列表](#api-28)
  29. [GET 贵金属排行](#api-29)
  30. [GET 贵金属K线](#api-30)
  31. [GET 贵金属实时行情](#api-31)
  32. [GET 贵金属实时行情(整个市场)](#api-32)
  33. [GET 板块成分股](#api-33)
  34. [GET 实时行情(返回整个市场实时行情)](#api-34)
  35. [GET 板块列表](#api-35)
  36. [GET 板块排行](#api-36)
  37. [GET 板块K线](#api-37)
  38. [GET 实时行情](#api-38)
  39. [GET 股票清单](#api-39)
  40. [GET 资产负债表](#api-40)
  41. [GET 企业现金流](#api-41)
  42. [GET 企业现金流](#api-42)
  43. [GET 企业信息](#api-43)
  44. [GET 企业高管列表](#api-44)
  45. [GET 企业高管列表](#api-45)
  46. [GET 企业信息](#api-46)
  47. [GET 当日资金流向](#api-47)
  48. [GET 交易快照](#api-48)
  49. [GET 股票分红/送股/配股](#api-49)
  50. [GET 股票交易所](#api-50)
  51. [GET 财务信息](#api-51)
  52. [GET 企业利润表](#api-52)
  53. [GET 企业利润表](#api-53)
  54. [GET 资金流向](#api-54)
  55. [GET IPO新股上市](#api-55)
  56. [GET 个股股新闻](#api-56)
  57. [GET 券商研报](#api-57)
  58. [GET 企业管理层薪酬及持股](#api-58)
  59. [GET 历史股本](#api-59)
  60. [GET 股票排行](#api-60)
  61. [GET 股票清单](#api-61)
  62. [GET Top10流动股东](#api-62)
  63. [GET Top10股东/流动股东](#api-63)
  64. [GET Top10股东/流动股东](#api-64)
  65. [GET 股票K线](#api-65)
  66. [GET 实时行情](#api-66)
  67. [GET 实时行情(返回整个市场实时行情)](#api-67)
  68. [GET 国家/地区](#api-68)
  69. [GET 币种](#api-69)
  70. [GET 关键字搜索](#api-70)
  71. [GET 交易日历](#api-71)
- [ws](#ws)
  72. [GET 订阅实时行情](#api-72)

## api

### <a id="api-1"></a>1. GET 加密货币列表

| 属性 | 值 |
|------|----|
| **路径** | `/api/crypto/v1/cryptoList` |
| **方法** | `GET` |
| **适用版本** | 按量计费、免费版、个人版、专业版、企业版 |

**请求参数**:

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| `token` | query | string | 否 | token,通过登录获取 |
| `exchangeCode` | query | string (OKX) | 否 | 交易所代码，默认okx。（OKX：OKX） |

**成功响应 (200)**:

| 字段名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `msg` | 字符串 | 是 | 响应消息 |
| `code` | 字符串 | 是 | 代码 |
| `data` | 数组 | 是 | 响应数据 |
| `data[].code` | 字符串 | 是 | 代码 |
| `data[].name` | 字符串 | 是 | 名称 |
| `data[].type` | 字符串 | 是 | 类型：（STOCK：股票，INDEX：指数，FUND：基金，FOREX：外汇，CRYPTO：加密货币，SECTOR：板块，BOND：债券，FUTURE：期货） |
| `data[].exchangeCode` | 字符串 | 是 |  |
| `data[].chineseName` | 字符串 | 是 | 中文名称 |

**响应示例**:

```json
{
  "msg": "ok",
  "code": 200,
  "data": [
    {
      "code": "BANANA",
      "name": "BANANA",
      "type": "CRYPTO",
      "exchangeCode": "OKX"
    },
    {
      "code": "USDC",
      "name": "USD Coin",
      "chineseName": "USD Coin",
      "type": "CRYPTO",
      "exchangeCode": "OKX"
    }
  ]
}
```

---

### <a id="api-2"></a>2. GET 加密货币K线

| 属性 | 值 |
|------|----|
| **路径** | `/api/crypto/v1/kline` |
| **方法** | `GET` |
| **适用版本** | 按量计费、免费版（不含分钟级数据）、个人版（不含分钟级数据）、专业版、企业版 |

**请求参数**:

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| `token` | query | string | 否 | token,通过登录获取 |
| `symbol` | query | string | 否 | 加密货币代码。 |
| `type` | query | string (day, day5, d1, w1, m1, y1) | 是 | k线类型， day：当日1分钟，day5：最近5个交易日1分钟，d1：日K，w1：周K，m1：月K，y1：年K。 |
| `beginDate` | query | string | 否 | 起始日期。格式“yyyy-mm-dd hh:mm:ss”。 |
| `endDate` | query | string | 否 | 结束日期。格式“yyyy-mm-dd hh:mm:ss”。 |
| `order` | query | string (ASC, DESC) | 否 | 顺序：ASC 表升序从小到大排序，DESC 表降序从大到小排序（默认在不输入时间为默认倒序，只输入开始时间强制为升序，只输入结束时间强制为降序，同时输入开始时间和结束时间为默认为倒序） |
| `limit` | query | string | 否 | 数量，默认：10000。（最大为20000） |
| `format` | query | string (json, csv) | 否 | 格式,支持json格式和csv格式（默认json格式） |

**成功响应 (200)**:

| 字段名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `msg` | 字符串 | 是 | 响应消息 |
| `code` | 字符串 | 是 | 代码 |
| `data` | 数组 | 是 | 响应数据 |
| `data[].date` | 字符串 | 是 |  |
| `data[].close` | 字符串 | 是 |  |
| `data[].open` | 字符串 | 是 |  |
| `data[].high` | 字符串 | 是 |  |
| `data[].low` | 字符串 | 是 |  |
| `data[].preClose` | 字符串 | 是 |  |
| `data[].type` | 字符串 | 是 | 类型(STOCK：股票，INDEX：指数，FUND：基金，FOREX：外汇，CRYPTO：加密货币) |
| `data[].name` | 字符串 | 是 | 名称 |
| `data[].countryCode` | 字符串 | 是 | 国家/地区代码。详见国家/地区清单接口。 |
| `data[].exchangeCode` | 字符串 | 是 | 交易所代码。详见交易所清单接口。 |
| `data[].chineseName` | 字符串 | 是 | 中文名称（美股）。 |

**响应示例**:

```json
{
  "msg": "ok",
  "code": 200,
  "data": [
    {
      "date": "2026-06-25",
      "close": "60684.8",
      "open": "62741.6",
      "high": "63130.8",
      "low": "59019.7",
      "preClose": "60212"
    },
    {
      "date": "2026-06-24",
      "close": "60212",
      "open": "62420.9",
      "high": "63162",
      "low": "60188.1",
      "preClose": "62394.2",
      "volume": "313.29803504",
      "amount": "19395737.62045597"
    }
  ]
}
```

---

### <a id="api-3"></a>3. GET 实时行情(返回整个市场实时行情)

| 属性 | 值 |
|------|----|
| **路径** | `/api/crypto/v1/realtimeMarket` |
| **方法** | `GET` |
| **适用版本** | 企业版 |

**请求参数**:

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| `token` | query | string | 否 | token,通过登录获取 |
| `exchangeCode` | query | string (OKX) | 否 | 交易所代码，默认okx。（OKX：OKX） |
| `fields` | query | string | 否 | 返回的字段，中间以逗号分隔，字段名称点击”响应Response“可查看，输入all默认返回所有数据。 |
| `format` | query | string (json, csv) | 否 | 格式,支持json格式和csv格式（默认json格式） |

**成功响应 (200)**:

| 字段名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `msg` | 字符串 | 是 | 响应消息 |
| `code` | 字符串 | 是 | 代码 |
| `data` | 数组 | 是 | 响应数据 |
| `data[].code` | 字符串 | 是 | 代码 |
| `data[].exchangeCode` | 字符串 | 是 | 交易所代码。详见交易所清单接口。 |
| `data[].high` | 字符串 | 是 | 最高价 |
| `data[].low` | 字符串 | 是 | 最低价 |
| `data[].name` | 字符串 | 是 | 名称 |
| `data[].open` | 字符串 | 是 | 开盘价 |
| `data[].price` | 字符串 | 是 | 价格 |
| `data[].type` | 字符串 | 是 | 类型(STOCK：股票，INDEX：指数，FUND：基金，FOREX：外汇，CRYPTO：加密货币) |
| `data[].countryCode` | 字符串 | 是 | 国家/地区代码。详见国家/地区清单接口。 |
| `data[].chineseName` | 字符串 | 是 | 中文名称（美股）。 |
| `data[].localDate` | 字符串 | 是 | 更新时间。 |
| `data[].preClose` | 字符串 | 是 | 收盘价 |
| `data[].volume` | 字符串 | 是 | 成交量 |
| `data[].amount` | 字符串 | 是 | 成交额 |
| `data[].change` | 字符串 | 是 | 涨跌额 |
| `data[].changeRate` | 字符串 | 是 | 涨跌幅 |
| `data[].activeSellVol` | 整数 | 是 | 内盘(主动卖出总量) |
| `data[].activeBuyVol` | 整数 | 是 | 外盘(主动买入总量) |
| `data[].floatCap` | 字符串 | 是 | 流通市值 |
| `data[].mktCap` | 字符串 | 是 | 总市值 |
| `data[].floatShr` | 字符串 | 是 | 流通股本 |
| `data[].totShr` | 字符串 | 是 | 总股本 |
| `data[].ordImbRatio` | 字符串 | 是 | 委比 |
| `data[].pb` | 字符串 | 是 | 市净率 |
| `data[].turnover` | 字符串 | 是 | 换手率 |
| `data[].pe_ttm` | 字符串 | 是 | TTM市盈率 |
| `data[].pe_dyn` | 字符串 | 是 | 动态市盈率 |
| `data[].pe_static` | 字符串 | 是 | 静态市盈率 |
| `data[].amplitude` | 字符串 | 是 | 振幅 |
| `data[].highLimit` | 字符串 | 是 | 涨停价格 |
| `data[].lowLimit` | 字符串 | 是 | 跌停价格 |
| `data[].askPx1` | 实数 | 是 | 卖一价 |
| `data[].askVol1` | 整数 | 是 | 卖一量 |
| `data[].askPx2` | 实数 | 是 | 卖二价 |
| `data[].askVol2` | 整数 | 是 | 卖二量 |
| `data[].askPx3` | 实数 | 是 | 卖三价 |
| `data[].askVol3` | 整数 | 是 | 卖三量 |
| `data[].askPx4` | 实数 | 是 | 卖四价 |
| `data[].askVol4` | 整数 | 是 | 卖四量 |
| `data[].askPx5` | 实数 | 是 | 卖五价 |
| `data[].askVol5` | 整数 | 是 | 卖五量 |
| `data[].bidPx1` | 实数 | 是 | 买一价 |
| `data[].bidVol1` | 整数 | 是 | 买一量 |
| `data[].bidPx2` | 实数 | 是 | 买二价 |
| `data[].bidVol2` | 整数 | 是 | 买二量 |
| `data[].bidPx3` | 实数 | 是 | 买三价 |
| `data[].bidVol3` | 整数 | 是 | 买三量 |
| `data[].bidPx4` | 实数 | 是 | 买四价 |
| `data[].bidVol4` | 整数 | 是 | 买四量 |
| `data[].bidPx5` | 实数 | 是 | 买五价 |
| `data[].bidVol5` | 整数 | 是 | 买五量 |

**响应示例**:

```json
{
  "msg": "ok",
  "code": 200,
  "data": [
    {
      "code": "CFX",
      "exchangeCode": "OKX",
      "high": "0.04647",
      "low": "0.04229",
      "name": "CFX",
      "open": "0.04623",
      "price": "0.04369"
    },
    {
      "code": "MOVE",
      "exchangeCode": "OKX",
      "high": "0.01139",
      "low": "0.01047",
      "name": "MOVE",
      "open": "0.01118",
      "price": "0.01113"
    }
  ]
}
```

---

### <a id="api-4"></a>4. GET 加密货币排序

| 属性 | 值 |
|------|----|
| **路径** | `/api/crypto/v1/sort` |
| **方法** | `GET` |
| **适用版本** | 按量计费、专业版、企业版 |

**请求参数**:

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| `token` | query | string | 否 | token,通过登录获取 |
| `exchangeCode` | query | string (OKX) | 否 | 交易所代码，默认okx。（OKX：OKX） |
| `sort` | query | string (price, change, changeRate, volume, amount, circulationValue, circulationShares, amplitude, open, high, low, preClose) | 是 | 排序方式。
（price：价格，change：涨跌额，changeRate：涨跌幅，volume：成交量，amount：成交额，
                    circulationValue：流通市值，circulationShares：流通股本，amplitude：振幅，open：开盘价，high：最高价，low：最低价，preClose：昨收） |
| `order` | query | string (ASC, DESC) | 是 | 顺序：ASC 表升序，DESC 表降序（默认DESC） |
| `page` | query | string | 否 | 第几页，每页100行数据 |
| `format` | query | string (json, csv) | 否 | 格式,支持json格式和csv格式（默认json格式） |

**成功响应 (200)**:

| 字段名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `msg` | 字符串 | 是 | 响应消息 |
| `code` | 字符串 | 是 | 代码 |
| `data` | 对象 | 是 | 响应数据 |
| `data.pageNum` | 整数 | 是 |  |
| `data.pageTotal` | 整数 | 是 |  |
| `data.countTotal` | 整数 | 是 |  |
| `data.list` | 数组 | 是 |  |
| `data.list[].code` | 字符串 | 是 | 代码 |
| `data.list[].name` | 字符串 | 是 | 名称 |
| `data.list[].type` | 字符串 | 是 | 类型(STOCK：股票，INDEX：指数，FUND：基金，FOREX：外汇，CRYPTO：加密货币) |
| `data.list[].exchangeCode` | 字符串 | 是 | 交易所代码。详见交易所清单接口。 |
| `data.list[].timestamp` | 整数 | 是 |  |
| `data.list[].localDate` | 字符串 | 是 |  |
| `data.list[].price` | 字符串 | 是 |  |
| `data.list[].open` | 字符串 | 是 |  |
| `data.list[].high` | 字符串 | 是 |  |
| `data.list[].low` | 字符串 | 是 |  |
| `data.list[].change` | 字符串 | 是 |  |
| `data.list[].changeRate` | 字符串 | 是 |  |
| `data.list[].amplitude` | 实数 | 是 |  |
| `data.countryCode` | 字符串 | 是 | 国家/地区代码。详见国家/地区清单接口。 |
| `data.chineseName` | 字符串 | 是 | 中文名称（美股）。 |

**响应示例**:

```json
{
  "msg": "ok",
  "code": 200,
  "data": {
    "pageNum": 1,
    "pageTotal": 6,
    "countTotal": 297,
    "list": [
      {
        "code": "ID",
        "name": "ID",
        "type": "CRYPTO",
        "exchangeCode": "OKX",
        "timestamp": 1782350199191,
        "localDate": "2026-06-25 01:16:39",
        "price": "0.04109",
        "open": "0.03525",
        "high": "0.04179",
        "low": "0.03447",
        "change": "0.0058",
        "changeRate": "16.5674",
        "amplitude": 17.8146
      },
      {
        "code": "SAHARA",
        "name": "SAHARA",
        "type": "CRYPTO",
        "exchangeCode": "OKX",
        "timestamp": 1782350200531,
        "localDate": "2026-06-25 01:16:40",
        "price": "0.01367",
        "open": "0.01205",
        "high": "0.01456",
        "low": "0.01193",
        "change": "0.0016",
        "changeRate": "13.444",
        "amplitude": 19.2392
      }
    ]
  }
}
```

---

### <a id="api-5"></a>5. GET 实时行情

| 属性 | 值 |
|------|----|
| **路径** | `/api/crypto/v2/realtime` |
| **方法** | `GET` |
| **适用版本** | 按量计费、专业版、企业版 |

**请求参数**:

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| `token` | query | string | 否 | token,通过登录获取 |
| `symbol` | query | string | 否 | 加密货币代码，支持多个最多一次20个行情数据用英文逗号隔开。采用代码加交易所代码或简称，不加交易所默认okx，（OKX：欧易，BNB：币安，HT：火币） |

**成功响应 (200)**:

| 字段名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `msg` | 字符串 | 是 | 响应消息 |
| `code` | 字符串 | 是 | 代码 |
| `data` | 数组 | 是 | 响应数据 |
| `data[].code` | 字符串 | 是 | 代码 |
| `data[].name` | 字符串 | 是 | 名称 |
| `data[].chineseName` | 字符串 | 是 | 中文名称（美股）。 |
| `data[].type` | 字符串 | 是 | 类型(STOCK：股票，INDEX：指数，FUND：基金，FOREX：外汇，CRYPTO：加密货币) |
| `data[].exchangeCode` | 字符串 | 是 | 交易所代码。详见交易所清单接口。 |
| `data[].timestamp` | 整数 | 是 |  |
| `data[].localDate` | 字符串 | 是 |  |
| `data[].price` | 字符串 | 是 |  |
| `data[].open` | 字符串 | 是 |  |
| `data[].high` | 字符串 | 是 |  |
| `data[].low` | 字符串 | 是 |  |
| `data[].change` | 字符串 | 是 |  |
| `data[].changeRate` | 字符串 | 是 |  |
| `data[].amplitude` | 实数 | 是 |  |
| `data[].countryCode` | 字符串 | 是 | 国家/地区代码。详见国家/地区清单接口。 |

**响应示例**:

```json
{
  "msg": "ok",
  "code": 200,
  "data": [
    {
      "code": "BTC",
      "name": "Bitcoin",
      "chineseName": "比特币",
      "type": "CRYPTO",
      "exchangeCode": "OKX",
      "timestamp": 1782350200265,
      "localDate": "2026-06-25 01:16:40",
      "price": "60689",
      "open": "62741.6",
      "high": "63130.8",
      "low": "59019.7",
      "change": "-2052.6",
      "changeRate": "-3.2715",
      "amplitude": 6.774
    },
    {
      "code": "ETC",
      "name": "Ethereum Classic",
      "chineseName": "以太经典",
      "type": "CRYPTO",
      "exchangeCode": "OKX",
      "timestamp": 1782350200264,
      "localDate": "2026-06-25 01:16:40",
      "price": "7.044",
      "open": "7.078",
      "high": "7.168",
      "low": "6.608",
      "change": "-0.034",
      "changeRate": "-0.4804",
      "amplitude": 7.95
    }
  ]
}
```

---

### <a id="api-6"></a>6. GET 外汇列表

| 属性 | 值 |
|------|----|
| **路径** | `/api/forex/v1/forexList` |
| **方法** | `GET` |
| **适用版本** | 按量计费、免费版、个人版、专业版、企业版 |

**请求参数**:

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| `token` | query | string | 否 | token,通过登录获取 |
| `exchangeCode` | query | string (FXCM) | 否 | 交易所代码，默认FXCM。 |

**成功响应 (200)**:

| 字段名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `msg` | 字符串 | 是 | 响应消息 |
| `code` | 字符串 | 是 | 代码 |
| `data` | 数组 | 是 | 响应数据 |
| `data[].code` | 字符串 | 是 | 代码 |
| `data[].name` | 字符串 | 是 | 名称 |
| `data[].chineseName` | 字符串 | 是 |  |
| `data[].type` | 字符串 | 是 | 类型(FOREX：外汇) |
| `data[].exchangeCode` | 字符串 | 是 | 交易所代码 |

**响应示例**:

```json
{
  "msg": "ok",
  "code": 200,
  "data": [
    {
      "code": "AUDNZD",
      "name": "澳元新西兰元",
      "chineseName": "澳元新西兰元",
      "type": "FOREX",
      "exchangeCode": "FXCM"
    },
    {
      "code": "CHFJPY",
      "name": "瑞郎日元",
      "chineseName": "瑞郎日元",
      "type": "FOREX",
      "exchangeCode": "FXCM"
    }
  ]
}
```

---

### <a id="api-7"></a>7. GET 外汇排行

| 属性 | 值 |
|------|----|
| **路径** | `/api/forex/v1/sort` |
| **方法** | `GET` |
| **适用版本** | 专业版、企业版 |

**请求参数**:

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| `token` | query | string | 否 | token,通过登录获取 |
| `exchangeCode` | query | string (FXCM) | 否 | 交易所代码，默认FXCM。 |
| `sort` | query | string (price, change, changeRate, open, high, low, preClose) | 是 | 排序字段。 |
| `order` | query | string (asc, desc) | 否 | 排序方向，asc或desc。 |
| `page` | query | string | 否 | 页码。 |

**成功响应 (200)**:

| 字段名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `msg` | 字符串 | 是 | 响应消息 |
| `code` | 整数 | 是 | 响应状态码，200 表示成功 |
| `data` | 对象 | 是 | 响应数据 |
| `data.pageNum` | 整数 | 是 | 当前页 |
| `data.pageTotal` | 整数 | 是 | 总页数 |
| `data.countTotal` | 整数 | 是 | 总数量 |
| `data.list` | 数组 | 是 | 排行数据 |
| `data.list[].code` | 字符串 | 是 |  |
| `data.list[].name` | 字符串 | 是 |  |
| `data.list[].chineseName` | 字符串 | 是 |  |
| `data.list[].type` | 字符串 | 是 |  |
| `data.list[].exchangeCode` | 字符串 | 是 |  |
| `data.list[].timestamp` | 整数 | 是 |  |
| `data.list[].localDate` | 字符串 | 是 |  |
| `data.list[].price` | 字符串 | 是 |  |
| `data.list[].open` | 字符串 | 是 |  |
| `data.list[].high` | 字符串 | 是 |  |
| `data.list[].low` | 字符串 | 是 |  |
| `data.list[].preClose` | 字符串 | 是 |  |
| `data.list[].volume` | 字符串 | 是 |  |
| `data.list[].amount` | 字符串 | 是 |  |
| `data.list[].change` | 字符串 | 是 |  |
| `data.list[].changeRate` | 字符串 | 是 |  |
| `data.list[].mktCap` | 字符串 | 是 |  |
| `data.list[].floatCap` | 字符串 | 是 |  |
| `data.list[].totShr` | 字符串 | 是 |  |
| `data.list[].floatShr` | 字符串 | 是 |  |
| `data.list[].amplitude` | 实数 | 是 |  |

**响应示例**:

```json
{
  "msg": "ok",
  "code": 200,
  "data": {
    "pageNum": 1,
    "pageTotal": 1,
    "countTotal": 40,
    "list": [
      {
        "code": "EURTRY",
        "name": "欧元兑土耳其里拉",
        "chineseName": "欧元兑土耳其里拉",
        "type": "FOREX",
        "exchangeCode": "FXCM",
        "timestamp": 1782350201000,
        "localDate": "2026-06-25 09:16:41",
        "price": "52.9044",
        "open": "52.8905",
        "high": "52.9568",
        "low": "52.8421",
        "preClose": "52.8369",
        "volume": "0",
        "amount": "0",
        "change": "0.0675",
        "changeRate": "0.1278",
        "mktCap": "0",
        "floatCap": "0",
        "totShr": "0",
        "floatShr": "0",
        "amplitude": 0.217
      },
      {
        "code": "GBPAUD",
        "name": "英镑澳元",
        "chineseName": "英镑澳元",
        "type": "FOREX",
        "exchangeCode": "FXCM",
        "timestamp": 1782350201000,
        "localDate": "2026-06-25 09:16:41",
        "price": "1.9099",
        "open": "1.909",
        "high": "1.9107",
        "low": "1.9055",
        "preClose": "1.9082",
        "volume": "0",
        "amount": "0",
        "change": "0.0017",
        "changeRate": "0.0891",
        "mktCap": "0",
        "floatCap": "0",
        "totShr": "0",
        "floatShr": "0",
        "amplitude": 0.2725
      }
    ]
  }
}
```

---

### <a id="api-8"></a>8. GET 外汇K线

| 属性 | 值 |
|------|----|
| **路径** | `/api/forex/v2/kline` |
| **方法** | `GET` |
| **适用版本** | 按量计费、免费版、个人版、专业版、企业版 |

**请求参数**:

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| `token` | query | string | 否 | token,通过登录获取 |
| `symbol` | query | string | 是 | 外汇代码。 |
| `type` | query | string (day, day5, d1, w1, m1, y1) | 是 | K线类型，day：当日1分钟，day5：最近5个交易日1分钟，d1：日K，w1：周K，m1：月K，y1：年K。 |
| `beginDate` | query | string | 否 | 起始日期。格式“yyyy-mm-dd hh:mm:ss”。 |
| `endDate` | query | string | 否 | 结束日期。格式“yyyy-mm-dd hh:mm:ss”。 |
| `format` | query | string (json, csv) | 否 | 格式,支持json格式和csv格式（默认json格式） |

**成功响应 (200)**:

| 字段名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `msg` | 字符串 | 是 | 响应消息 |
| `code` | 整数 | 是 | 响应状态码，200 表示成功 |
| `data` | 数组 | 是 | 响应数据 |
| `data[].date` | 字符串 | 是 | 交易日 |
| `data[].open` | 浮点数 | 是 | 开盘价 |
| `data[].high` | 浮点数 | 是 | 最高价 |
| `data[].low` | 浮点数 | 是 | 最低价 |
| `data[].close` | 浮点数 | 是 | 收盘价 |

**响应示例**:

```json
{
  "msg": "ok",
  "code": 200,
  "data": []
}
```

---

### <a id="api-9"></a>9. GET 外汇实时行情

| 属性 | 值 |
|------|----|
| **路径** | `/api/forex/v2/realtime` |
| **方法** | `GET` |
| **适用版本** | 专业版、企业版 |

**请求参数**:

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| `token` | query | string | 否 | token,通过登录获取 |
| `symbol` | query | string | 是 | 外汇代码，多个代码用英文逗号分隔。 |
| `format` | query | string (json, csv) | 否 | 格式,支持json格式和csv格式（默认json格式） |

**成功响应 (200)**:

| 字段名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `msg` | 字符串 | 是 | 响应消息 |
| `code` | 字符串 | 是 | 代码 |
| `data` | 数组 | 是 | 响应数据 |
| `data[].code` | 字符串 | 是 | 代码 |
| `data[].name` | 字符串 | 是 |  |
| `data[].chineseName` | 字符串 | 是 |  |
| `data[].type` | 字符串 | 是 | 类型(FOREX：外汇) |
| `data[].exchangeCode` | 字符串 | 是 |  |
| `data[].timestamp` | 整数 | 是 |  |
| `data[].localDate` | 字符串 | 是 |  |
| `data[].price` | 浮点数 | 是 | 最新价 |
| `data[].open` | 字符串 | 是 |  |
| `data[].high` | 字符串 | 是 |  |
| `data[].low` | 字符串 | 是 |  |
| `data[].preClose` | 字符串 | 是 |  |
| `data[].volume` | 字符串 | 是 |  |
| `data[].amount` | 字符串 | 是 |  |
| `data[].change` | 字符串 | 是 |  |
| `data[].changeRate` | 字符串 | 是 |  |
| `data[].mktCap` | 字符串 | 是 |  |
| `data[].floatCap` | 字符串 | 是 |  |
| `data[].totShr` | 字符串 | 是 |  |
| `data[].floatShr` | 字符串 | 是 |  |
| `data[].amplitude` | 实数 | 是 |  |

**响应示例**:

```json
{
  "msg": "ok",
  "code": 200,
  "data": [
    {
      "code": "EURUSD",
      "name": "欧元美元",
      "chineseName": "欧元美元",
      "type": "FOREX",
      "exchangeCode": "FXCM",
      "timestamp": 1782350201000,
      "localDate": "2026-06-25 09:16:41",
      "price": "1.1361",
      "open": "1.1359",
      "high": "1.1364",
      "low": "1.1348",
      "preClose": "1.1359",
      "volume": "0",
      "amount": "0",
      "change": "0.0002",
      "changeRate": "0.0176",
      "mktCap": "0",
      "floatCap": "0",
      "totShr": "0",
      "floatShr": "0",
      "amplitude": 0.1408
    },
    {
      "code": "USDCNH",
      "name": "美元人民币",
      "chineseName": "美元人民币",
      "type": "FOREX",
      "exchangeCode": "FXCM",
      "timestamp": 1782350201000,
      "localDate": "2026-06-25 09:16:41",
      "price": "6.8087",
      "open": "6.8132",
      "high": "6.8138",
      "low": "6.8081",
      "preClose": "6.8132",
      "volume": "0",
      "amount": "0",
      "change": "-0.0045",
      "changeRate": "-0.066",
      "mktCap": "0",
      "floatCap": "0",
      "totShr": "0",
      "floatShr": "0",
      "amplitude": 0.0836
    }
  ]
}
```

---

### <a id="api-10"></a>10. GET 外汇实时行情(整个市场)

| 属性 | 值 |
|------|----|
| **路径** | `/api/forex/v2/realtimeMarket` |
| **方法** | `GET` |
| **适用版本** | 企业版 |

**请求参数**:

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| `token` | query | string | 否 | token,通过登录获取 |
| `exchangeCode` | query | string (FXCM) | 否 | 交易所代码，默认FXCM。 |
| `fields` | query | string | 否 | 返回字段，多个字段用英文逗号分隔，all表示全部字段。 |
| `format` | query | string (json, csv) | 否 | 格式,支持json格式和csv格式（默认json格式） |

**成功响应 (200)**:

| 字段名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `msg` | 字符串 | 是 | 响应消息 |
| `code` | 字符串 | 是 | 代码 |
| `data` | 数组 | 是 | 响应数据 |
| `data[].amount` | 字符串 | 是 |  |
| `data[].amplitude` | 实数 | 是 |  |
| `data[].bondtype` | 字符串 | 是 |  |
| `data[].change` | 字符串 | 是 |  |
| `data[].changerate` | 字符串 | 是 |  |
| `data[].chinesename` | 字符串 | 是 |  |
| `data[].code` | 字符串 | 是 | 代码 |
| `data[].countrycode` | 字符串 | 是 |  |
| `data[].exchangecode` | 字符串 | 是 |  |
| `data[].floatcap` | 字符串 | 是 |  |
| `data[].floatshr` | 字符串 | 是 |  |
| `data[].fundtype` | 字符串 | 是 |  |
| `data[].high` | 字符串 | 是 |  |
| `data[].localdate` | 字符串 | 是 |  |
| `data[].low` | 字符串 | 是 |  |
| `data[].mktcap` | 字符串 | 是 |  |
| `data[].name` | 字符串 | 是 |  |
| `data[].open` | 字符串 | 是 |  |
| `data[].preclose` | 字符串 | 是 |  |
| `data[].price` | 浮点数 | 是 | 最新价 |
| `data[].sectortype` | 字符串 | 是 |  |
| `data[].timestamp` | 整数 | 是 |  |
| `data[].totshr` | 字符串 | 是 |  |
| `data[].type` | 字符串 | 是 | 类型(FOREX：外汇) |
| `data[].updatetime` | 整数 | 是 |  |
| `data[].volume` | 字符串 | 是 |  |

**响应示例**:

```json
{
  "msg": "ok",
  "code": 200,
  "data": [
    {
      "amount": "0",
      "amplitude": 0.1408,
      "bondtype": "",
      "change": "0.0002",
      "changerate": "0.0176",
      "chinesename": "欧元美元",
      "code": "EURUSD",
      "countrycode": "",
      "exchangecode": "FXCM",
      "floatcap": "0",
      "floatshr": "0",
      "fundtype": "",
      "high": "1.1364",
      "localdate": "2026-06-25 09:16:41",
      "low": "1.1348",
      "mktcap": "0",
      "name": "欧元美元",
      "open": "1.1359",
      "preclose": "1.1359",
      "price": "1.1361",
      "sectortype": "",
      "timestamp": 1782350201000,
      "totshr": "0",
      "type": "FOREX",
      "updatetime": 0,
      "volume": "0"
    },
    {
      "amount": "0",
      "amplitude": 0.0836,
      "bondtype": "",
      "change": "-0.0045",
      "changerate": "-0.066",
      "chinesename": "美元人民币",
      "code": "USDCNH",
      "countrycode": "",
      "exchangecode": "FXCM",
      "floatcap": "0",
      "floatshr": "0",
      "fundtype": "",
      "high": "6.8138",
      "localdate": "2026-06-25 09:16:41",
      "low": "6.8081",
      "mktcap": "0",
      "name": "美元人民币",
      "open": "6.8132",
      "preclose": "6.8132",
      "price": "6.8087",
      "sectortype": "",
      "timestamp": 1782350201000,
      "totshr": "0",
      "type": "FOREX",
      "updatetime": 0,
      "volume": "0"
    }
  ]
}
```

---

### <a id="api-11"></a>11. GET 基金资产配置

| 属性 | 值 |
|------|----|
| **路径** | `/api/fund/v1/assetAllocation` |
| **方法** | `GET` |
| **适用版本** | 按量计费、免费版、个人版、专业版、企业版 |

**请求参数**:

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| `token` | query | string | 否 | token,通过登录获取 |
| `symbol` | query | string | 是 | 基金代码 |

**成功响应 (200)**:

| 字段名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `msg` | 字符串 | 是 | 响应消息 |
| `code` | 字符串 | 是 | 代码 |
| `data` | 对象 | 是 | 响应数据 |
| `data.page` | 整数 | 是 |  |
| `data.pageTotal` | 整数 | 是 |  |
| `data.countTotal` | 整数 | 是 |  |
| `data.list` | 数组 | 是 |  |
| `data.list[].ticker` | 对象 | 是 |  |
| `data.list[].ticker.code` | 字符串 | 是 | 代码 |
| `data.list[].ticker.name` | 字符串 | 是 | 名称 |
| `data.list[].ticker.countryCode` | 字符串 | 是 | 国家/地区代码。详见国家/地区清单接口。 |
| `data.list[].ticker.exchangeCode` | 字符串 | 是 | 交易所代码。详见交易所清单接口。 |
| `data.list[].ticker.type` | 字符串 | 是 | 类型(FUND：基金) |
| `data.list[].ticker.fundType` | 字符串 | 是 |  |
| `data.list[].data` | 对象 | 是 |  |
| `data.list[].data.date` | 字符串 | 是 | 时间。 |
| `data.list[].data.price` | 字符串 | 是 | 价格。 |
| `data.list[].data.preClose` | 字符串 | 是 | 昨收。 |
| `data.list[].data.open` | 字符串 | 是 | 开盘价。 |
| `data.list[].data.high` | 实数 | 是 | 最高价。 |
| `data.list[].data.low` | 实数 | 是 | 最低价。 |
| `data.list[].data.change` | 实数 | 是 | 涨跌额。 |
| `data.list[].data.changeRate` | 实数 | 是 | 涨跌幅。 |
| `data.list[].data.amplitude` | 实数 | 是 | 振幅。 |
| `data.list[].data.highLimit` | 实数 | 是 | 涨停价。 |
| `data.list[].data.lowLimit` | 实数 | 是 | 跌停价。 |
| `data.list[].data.volume` | 实数 | 是 | 成交量。 |
| `data.list[].data.amount` | 实数 | 是 | 成交额。 |
| `data.list[].data.sellVolume` | 实数 | 是 | 卖盘。 |
| `data.list[].data.buyVolume` | 实数 | 是 | 买盘。 |
| `data.list[].data.pb` | 整数 | 是 |  |
| `data.list[].data.vr` | 实数 | 是 | 量比。 |
| `data.list[].data.iopv` | 实数 | 是 | iopv(ETF)。 |
| `data.list[].data.committee` | 实数 | 是 | 委比。 |
| `data.list[].data.circulationValue` | 实数 | 是 | 流通规模。 |
| `data.list[].data.marketValue` | 实数 | 是 | 总市值。 |
| `data.list[].data.circulationShares` | 实数 | 是 | 流通市值。 |
| `data.list[].data.totalShares` | 实数 | 是 | 总份额。 |
| `data.list[].data.turnover` | 实数 | 是 | 换手率。 |
| `data.list[].data.sells` | 数组 | 是 |  |
| `data.list[].data.buys` | 数组 | 是 |  |
| `data.chineseName` | 字符串 | 是 | 中文名称（美股）。 |

**响应示例**:

```json
{
  "msg": "ok",
  "code": 200,
  "data": {
    "page": 1,
    "pageTotal": 3,
    "countTotal": 240,
    "list": [
      {
        "ticker": {
          "code": "520500",
          "name": "恒生创新药ETF",
          "countryCode": "CHN",
          "exchangeCode": "XSHG",
          "type": "FUND",
          "fundType": "ETF"
        },
        "data": {
          "date": "2025-05-22 16:04:09",
          "price": 1.301,
          "preClose": 1.23,
          "open": 1.236,
          "high": 1.31,
          "low": 1.236,
          "change": 0.071,
          "changeRate": 5.77235772357723,
          "amplitude": 6.02,
          "highLimit": 1.353,
          "lowLimit": 1.107,
          "volume": 643406300,
          "amount": 826793598,
          "sellVolume": 334530200,
          "buyVolume": 308876100,
          "pb": 0,
          "vr": 3.39,
          "iopv": 1.3067,
          "committee": 23.37,
          "circulationValue": 397852305,
          "marketValue": 397852305,
          "circulationShares": 305805000,
          "totalShares": 305805000,
          "turnover": 210.4,
          "sells": [
            {
              "price": 1.302,
              "volume": 86100
            },
            {
              "price": 1.301,
              "volume": 387700
            },
            {
              "price": 1.3,
              "volume": 1085900
            },
            {
              "price": 1.299,
              "volume": 1007900
            },
            {
              "price": 1.298,
              "volume": 194400
            }
          ],
          "buys": [
            {
              "price": 1.303,
              "volume": 451500
            },
            {
              "price": 1.304,
              "volume": 448800
            },
            {
              "price": 1.305,
              "volume": 565100
            },
            {
              "price": 1.306,
              "volume": 189600
            },
            {
              "price": 1.307,
              "volume": 60600
            }
          ]
        }
      },
      {
        "ticker": {
          "code": "159316",
          "name": "恒生创新药ETF",
          "countryCode": "CHN",
          "exchangeCode": "XSHE",
          "type": "FUND",
          "fundType": "ETF"
        },
        "data": {
          "date": "2025-05-22 16:04:05",
          "price": 1.021,
          "preClose": 0.966,
          "open": 0.981,
          "high": 1.03,
          "low": 0.97,
          "change": 0.0549999999999999,
          "changeRate": 5.6935817805383,
          "amplitude": 6.21,
          "highLimit": 1.063,
          "lowLimit": 0.869,
          "volume": 375717700,
          "amount": 380654621,
          "sellVolume": 198574900,
          "buyVolume": 177142800,
          "pb": 0,
          "vr": 10.21,
          "iopv": 1.0268,
          "committee": -1.48,
          "circulationValue": 184123197.919,
          "marketValue": 184123197.919,
          "circulationShares": 180336139,
          "totalShares": 180336139,
          "turnover": 208.34,
          "sells": [
            {
              "price": 1.021,
              "volume": 882900
            },
            {
              "price": 1.02,
              "volume": 1529900
            },
            {
              "price": 1.019,
              "volume": 199700
            },
            {
              "price": 1.018,
              "volume": 967800
            },
            {
              "price": 1.017,
              "volume": 52500
            }
          ],
          "buys": [
            {
              "price": 1.022,
              "volume": 543300
            },
            {
              "price": 1.023,
              "volume": 155400
            },
            {
              "price": 1.024,
              "volume": 1129300
            },
            {
              "price": 1.025,
              "volume": 773700
            },
            {
              "price": 1.026,
              "volume": 1140500
            }
          ]
        }
      }
    ]
  }
}
```

---

### <a id="api-12"></a>12. GET 基金列表

| 属性 | 值 |
|------|----|
| **路径** | `/api/fund/v1/fundList` |
| **方法** | `GET` |
| **适用版本** | 按量计费、免费版、个人版、专业版、企业版 |

**请求参数**:

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| `token` | query | string | 否 | token,通过登录获取 |
| `countryCode` | query | string (CHN) | 否 | 国家/地区代码。（默认CHN中国大陆） |
| `type` | query | string (all, close, lof, etf, money, reits) | 否 | 基金类型。（all:所有类型，close：封闭式基金，lof：LOF,etf：ETF，money：货币基金，reits：信托基金） |

**成功响应 (200)**:

| 字段名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `msg` | 字符串 | 是 | 响应消息 |
| `code` | 字符串 | 是 | 代码 |
| `data` | 数组 | 是 | 响应数据 |
| `data[].code` | 字符串 | 是 | 代码 |
| `data[].name` | 字符串 | 是 | 名称 |
| `data[].type` | 字符串 | 是 | 类型(FUND：基金) |
| `data[].fundType` | 字符串 | 是 | 基金类型。 |
| `data[].exchangeCode` | 字符串 | 是 | 交易所代码。详见交易所清单接口。 |
| `data[].countryCode` | 字符串 | 是 | 国家/地区代码。详见国家/地区清单接口。 |

**响应示例**:

```json
{
  "msg": "ok",
  "code": 200,
  "data": [
    {
      "code": "159703",
      "name": "新材料ETF天弘",
      "type": "FUND",
      "fundType": "ETF",
      "exchangeCode": "XSHE",
      "countryCode": "CHN"
    },
    {
      "code": "159625",
      "name": "绿色电力ETF嘉实",
      "type": "FUND",
      "fundType": "ETF",
      "exchangeCode": "XSHE",
      "countryCode": "CHN"
    }
  ]
}
```

---

### <a id="api-13"></a>13. GET 实时行情(返回整个市场实时行情)

| 属性 | 值 |
|------|----|
| **路径** | `/api/fund/v1/realtimeMarket` |
| **方法** | `GET` |
| **适用版本** | 企业版 |

**请求参数**:

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| `token` | query | string | 否 | token,通过登录获取 |
| `countryCode` | query | string (CHN) | 否 | 国家/地区代码，默认CHN。（CHN：中国大陆）） |
| `fundType` | query | string (close, lof, etf, reits) | 否 | 基金类型，默认ETF。（close：封闭式基金，lof：LOF,etf：ETF，reits：信托基金） |
| `fields` | query | string | 否 | 返回的字段，中间以逗号分隔，字段名称点击”响应Response“可查看，输入all默认返回所有数据。 |
| `format` | query | string (json, csv) | 否 | 格式,支持json格式和csv格式（默认json格式） |

**成功响应 (200)**:

| 字段名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `msg` | 字符串 | 是 | 响应消息 |
| `code` | 字符串 | 是 | 代码 |
| `data` | 数组 | 是 | 响应数据 |
| `data[].code` | 字符串 | 是 | 代码 |
| `data[].exchangeCode` | 字符串 | 是 | 交易所代码。详见交易所清单接口。 |
| `data[].high` | 实数 | 是 | 最高价。 |
| `data[].low` | 实数 | 是 | 最低价。 |
| `data[].name` | 字符串 | 是 | 名称 |
| `data[].open` | 字符串 | 是 | 开盘价。 |
| `data[].preClose` | 字符串 | 是 | 昨收。 |
| `data[].price` | 字符串 | 是 | 价格。 |
| `data[].type` | 字符串 | 是 | 类型(FUND：基金) |
| `data[].countryCode` | 字符串 | 是 | 国家/地区代码。详见国家/地区清单接口。 |
| `data[].chineseName` | 字符串 | 是 | 中文名称（美股）。 |
| `data[].localDate` | 字符串 | 是 | 时间。 |
| `data[].change` | 实数 | 是 | 涨跌额。 |
| `data[].changeRate` | 实数 | 是 | 涨跌幅。 |
| `data[].amplitude` | 实数 | 是 | 振幅。 |
| `data[].highLimit` | 实数 | 是 | 涨停价。 |
| `data[].lowLimit` | 实数 | 是 | 跌停价。 |
| `data[].volume` | 实数 | 是 | 成交量。 |
| `data[].amount` | 实数 | 是 | 成交额。 |
| `data[].activeSellVol` | 实数 | 是 | 卖盘。 |
| `data[].activeBuyVol` | 实数 | 是 | 买盘。 |
| `data[].volRatio` | 实数 | 是 | 量比。 |
| `data[].iopv` | 实数 | 是 | iopv(ETF) |
| `data[].ordImbRatio` | 实数 | 是 | 委比。 |
| `data[].floatCap` | 实数 | 是 | 流通规模。 |
| `data[].mktCap` | 实数 | 是 | 总市值。 |
| `data[].floatShr` | 实数 | 是 | 流通市值。 |
| `data[].totShr` | 实数 | 是 | 总份额。 |
| `data[].turnover` | 实数 | 是 | 换手率。 |

**响应示例**:

```json
{
  "msg": "ok",
  "code": 200,
  "data": [
    {
      "code": "520830",
      "exchangeCode": "XSHG",
      "high": "0",
      "low": "0",
      "name": "沙特ETF华泰柏瑞",
      "open": "0",
      "preClose": "0.902",
      "price": "0.901"
    },
    {
      "code": "515380",
      "exchangeCode": "XSHG",
      "high": "0",
      "low": "0",
      "name": "沪深300ETF泰康",
      "open": "0",
      "preClose": "5.778",
      "price": "5.778"
    }
  ]
}
```

---

### <a id="api-14"></a>14. GET 基金排序(不包含货币基金和开放式基金)

| 属性 | 值 |
|------|----|
| **路径** | `/api/fund/v1/sort` |
| **方法** | `GET` |
| **适用版本** | 按量计费、专业版、企业版 |

**请求参数**:

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| `token` | query | string | 否 | token,通过登录获取 |
| `countryCode` | query | string (CHN) | 否 | 国家/地区代码。（默认CHN中国大陆） |
| `market` | query | string (all, close, lof, etf, reits) | 是 | 基金类型。（all:所有类型(不包含开放式基金和货币基金)，close：封闭式基金，lof：LOF,etf：ETF，money：货币基金，reits：信托基金） |
| `sort` | query | string (price, change, changeRate, volume, amount, turnover, committee, circulationValue, marketValue, circulationShares, totalShares, amplitude, open, high, low, preClose) | 否 | 排序方式。
（price：价格，change：涨跌额，changeRate：涨跌幅，volume：成交量，amount：成交额，turnover：换手率，
                    ，committee：委比，circulationValue：流通市值，marketValue：总市值，circulationShares：流通股本，totalShares：总股本，amplitude：振幅，open：开盘价，high：最高价，low：最低价，preClose：昨收） |
| `order` | query | string (ASC, DESC) | 是 | 顺序：ASC 表升序，DESC 表降序（默认DESC） |
| `page` | query | string | 否 | 第几页，每页100行数据 |

**成功响应 (200)**:

| 字段名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `msg` | 字符串 | 是 | 响应消息 |
| `code` | 字符串 | 是 | 代码 |
| `data` | 对象 | 是 | 响应数据 |
| `data.pageNum` | 整数 | 是 |  |
| `data.pageTotal` | 整数 | 是 |  |
| `data.countTotal` | 整数 | 是 |  |
| `data.list` | 数组 | 是 |  |
| `data.list[].code` | 字符串 | 是 | 代码 |
| `data.list[].name` | 字符串 | 是 | 名称 |
| `data.list[].type` | 字符串 | 是 | 类型(FUND：基金) |
| `data.list[].fundType` | 字符串 | 是 |  |
| `data.list[].exchangeCode` | 字符串 | 是 | 交易所代码。详见交易所清单接口。 |
| `data.list[].countryCode` | 字符串 | 是 | 国家/地区代码。详见国家/地区清单接口。 |
| `data.list[].timestamp` | 整数 | 是 |  |
| `data.list[].localDate` | 字符串 | 是 | 时间。 |
| `data.list[].price` | 字符串 | 是 | 价格。 |
| `data.list[].open` | 字符串 | 是 | 开盘价。 |
| `data.list[].high` | 实数 | 是 | 最高价。 |
| `data.list[].low` | 实数 | 是 | 最低价。 |
| `data.list[].preClose` | 字符串 | 是 | 昨收。 |
| `data.list[].volume` | 实数 | 是 | 成交量。 |
| `data.list[].amount` | 实数 | 是 | 成交额。 |
| `data.list[].change` | 实数 | 是 | 涨跌额。 |
| `data.list[].changeRate` | 实数 | 是 | 涨跌幅。 |
| `data.list[].bidPx1` | 字符串 | 是 |  |
| `data.list[].bidPx2` | 字符串 | 是 |  |
| `data.list[].bidPx3` | 字符串 | 是 |  |
| `data.list[].bidPx4` | 字符串 | 是 |  |
| `data.list[].bidPx5` | 字符串 | 是 |  |
| `data.list[].bidVol1` | 整数 | 是 |  |
| `data.list[].bidVol2` | 整数 | 是 |  |
| `data.list[].bidVol3` | 整数 | 是 |  |
| `data.list[].bidVol4` | 整数 | 是 |  |
| `data.list[].bidVol5` | 整数 | 是 |  |
| `data.list[].askPx1` | 字符串 | 是 |  |
| `data.list[].askPx2` | 字符串 | 是 |  |
| `data.list[].askPx3` | 字符串 | 是 |  |
| `data.list[].askPx4` | 字符串 | 是 |  |
| `data.list[].askPx5` | 字符串 | 是 |  |
| `data.list[].askVol1` | 整数 | 是 |  |
| `data.list[].askVol2` | 整数 | 是 |  |
| `data.list[].askVol3` | 整数 | 是 |  |
| `data.list[].askVol4` | 整数 | 是 |  |
| `data.list[].askVol5` | 整数 | 是 |  |
| `data.list[].mktCap` | 实数 | 是 | 总市值。 |
| `data.list[].floatCap` | 实数 | 是 | 流通规模。 |
| `data.list[].totShr` | 实数 | 是 | 总份额。 |
| `data.list[].floatShr` | 实数 | 是 | 流通市值。 |
| `data.list[].ordImbRatio` | 实数 | 是 | 委比。 |
| `data.list[].pb` | 整数 | 是 |  |
| `data.list[].volRatio` | 实数 | 是 | 量比。 |
| `data.list[].turnover` | 实数 | 是 | 换手率。 |
| `data.list[].amplitude` | 实数 | 是 | 振幅。 |
| `data.list[].highLimit` | 实数 | 是 | 涨停价。 |
| `data.list[].lowLimit` | 实数 | 是 | 跌停价。 |
| `data.chineseName` | 字符串 | 是 | 中文名称（美股）。 |
| `data.activeSellVol` | 实数 | 是 | 卖盘。 |
| `data.activeBuyVol` | 实数 | 是 | 买盘。 |
| `data.iopv` | 实数 | 是 | iopv(ETF) |

**响应示例**:

```json
{
  "msg": "ok",
  "code": 200,
  "data": {
    "pageNum": 1,
    "pageTotal": 31,
    "countTotal": 1507,
    "list": [
      {
        "code": "159804",
        "name": "创中盘88ETF国寿",
        "type": "FUND",
        "fundType": "ETF",
        "exchangeCode": "XSHE",
        "countryCode": "CHN",
        "timestamp": 1782350181000,
        "localDate": "2026-06-25 09:16:21",
        "price": "2.23",
        "open": "0",
        "high": "0",
        "low": "0",
        "preClose": "1.858",
        "volume": "0",
        "amount": "0",
        "change": "0.372",
        "changeRate": "20.02",
        "bidPx1": "2.23",
        "bidPx2": "0",
        "bidPx3": "0",
        "bidPx4": "0",
        "bidPx5": "0",
        "bidVol1": 50800,
        "bidVol2": 0,
        "bidVol3": 0,
        "bidVol4": 0,
        "bidVol5": 0,
        "askPx1": "2.23",
        "askPx2": "0",
        "askPx3": "0",
        "askPx4": "0",
        "askPx5": "0",
        "askVol1": 50800,
        "askVol2": 800,
        "askVol3": 0,
        "askVol4": 0,
        "askVol5": 0,
        "mktCap": "53000000",
        "floatCap": "53000000",
        "totShr": "23899676",
        "floatShr": "23899676",
        "ordImbRatio": 0.78,
        "pb": 0,
        "volRatio": 0,
        "turnover": 0,
        "amplitude": 0,
        "highLimit": "2.23",
        "lowLimit": "1.486"
      },
      {
        "code": "159836",
        "name": "创业板300ETF天弘",
        "type": "FUND",
        "fundType": "ETF",
        "exchangeCode": "XSHE",
        "countryCode": "CHN",
        "timestamp": 1782350199000,
        "localDate": "2026-06-25 09:16:39",
        "price": "1.847",
        "open": "0",
        "high": "0",
        "low": "0",
        "preClose": "1.539",
        "volume": "0",
        "amount": "0",
        "change": "0.308",
        "changeRate": "20.01",
        "bidPx1": "1.847",
        "bidPx2": "0",
        "bidPx3": "0",
        "bidPx4": "0",
        "bidPx5": "0",
        "bidVol1": 10900,
        "bidVol2": 0,
        "bidVol3": 0,
        "bidVol4": 0,
        "bidVol5": 0,
        "askPx1": "1.847",
        "askPx2": "0",
        "askPx3": "0",
        "askPx4": "0",
        "askPx5": "0",
        "askVol1": 10900,
        "askVol2": 6000,
        "askVol3": 0,
        "askVol4": 0,
        "askVol5": 0,
        "mktCap": "177000000",
        "floatCap": "177000000",
        "totShr": "95747113",
        "floatShr": "95747113",
        "ordImbRatio": 21.58,
        "pb": 0,
        "volRatio": 0,
        "turnover": 0,
        "amplitude": 0,
        "highLimit": "1.847",
        "lowLimit": "1.231"
      }
    ]
  }
}
```

---

### <a id="api-15"></a>15. GET 基金K线

| 属性 | 值 |
|------|----|
| **路径** | `/api/fund/v2/kline` |
| **方法** | `GET` |
| **适用版本** | 按量计费、免费版（不含分钟级数据）、个人版（不含分钟级数据）、专业版、企业版 |

**请求参数**:

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| `token` | query | string | 否 | token,通过登录获取 |
| `symbol` | query | string | 是 | 股票代码，上证用sh开头，深证用sz开头，开放式用jj开头。 |
| `type` | query | string (day, day5, d1, w1, m1, y1) | 是 | k线类型， day：当日1分钟，day5：最近5个交易日1分钟，d1：日K，w1：周K，m1：月K，y1：年K。 |
| `beginDate` | query | string | 否 | 起始日期。格式“yyyy-mm-dd hh:mm:ss”。 |
| `endDate` | query | string | 否 | 结束日期。格式“yyyy-mm-dd hh:mm:ss”。 |
| `order` | query | string (ASC, DESC) | 否 | 顺序：ASC 表正序，DESC 表倒序（默认在不输入时间为倒序，只输入开始时间为正序，只输入结束时间为倒叙，输入开始时间和结束时间为倒序） |
| `limit` | query | string | 否 | 数量，默认：1000。（最大为2000） |
| `fq` | query | string (bfq, qfq) | 否 | 复权：默认不复权。（bfq 表不复权，qfq 表示前复权） |
| `format` | query | string (json, csv) | 否 | 格式,支持json格式和csv格式（默认json格式） |

**成功响应 (200)**:

| 字段名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `msg` | 字符串 | 是 | 响应消息 |
| `code` | 字符串 | 是 | 代码 |
| `data` | 数组 | 是 | 响应数据 |
| `data[].date` | 字符串 | 是 | 更新时间 |
| `data[].close` | 字符串 | 是 | 收盘价 |
| `data[].open` | 字符串 | 是 | 开盘价格 |
| `data[].high` | 字符串 | 是 | 最高价 |
| `data[].low` | 字符串 | 是 | 最低价 |
| `data[].preClose` | 字符串 | 是 | 昨收 |
| `data[].volume` | 字符串 | 是 | 成交量 |
| `data[].amount` | 字符串 | 是 | 成交额 |
| `data[].time` | 整数 | 是 | 时间戳(毫秒) |

**响应示例**:

```json
{
  "msg": "ok",
  "code": 200,
  "data": [
    {
      "date": "2026-06-25",
      "close": "1.341",
      "open": "0",
      "high": "0",
      "low": "0",
      "preClose": "1.35",
      "volume": "0",
      "amount": "0"
    },
    {
      "date": "2026-06-24",
      "close": "1.35",
      "open": "1.33",
      "high": "1.358",
      "low": "1.321",
      "preClose": "1.354",
      "volume": "21565100",
      "amount": "28886200"
    }
  ]
}
```

---

### <a id="api-16"></a>16. GET 实时行情

| 属性 | 值 |
|------|----|
| **路径** | `/api/fund/v2/realtime` |
| **方法** | `GET` |
| **适用版本** | 按量计费、专业版、企业版 |

**请求参数**:

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| `token` | query | string | 否 | token,通过登录获取 |
| `symbol` | query | string | 否 | 基金代码，支持多个最多一次20支基金数据用英文逗号隔开（上证用开头，深证用sz开头，开放式基金用jj开头）。 |

**成功响应 (200)**:

| 字段名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `msg` | 字符串 | 是 | 响应消息 |
| `code` | 字符串 | 是 | 代码 |
| `data` | 数组 | 是 | 响应数据 |
| `data[].code` | 字符串 | 是 | 代码 |
| `data[].name` | 字符串 | 是 | 名称 |
| `data[].type` | 字符串 | 是 | 类型(FUND：基金) |
| `data[].fundType` | 字符串 | 是 |  |
| `data[].exchangeCode` | 字符串 | 是 | 交易所代码。详见交易所清单接口。 |
| `data[].countryCode` | 字符串 | 是 | 国家/地区代码。详见国家/地区清单接口。 |
| `data[].timestamp` | 整数 | 是 |  |
| `data[].localDate` | 字符串 | 是 | 时间。 |
| `data[].price` | 字符串 | 是 | 价格。 |
| `data[].open` | 字符串 | 是 | 开盘价。 |
| `data[].high` | 实数 | 是 | 最高价。 |
| `data[].low` | 实数 | 是 | 最低价。 |
| `data[].preClose` | 字符串 | 是 | 昨收。 |
| `data[].volume` | 实数 | 是 | 成交量。 |
| `data[].amount` | 实数 | 是 | 成交额。 |
| `data[].change` | 实数 | 是 | 涨跌额。 |
| `data[].changeRate` | 实数 | 是 | 涨跌幅。 |
| `data[].bidPx1` | 字符串 | 是 |  |
| `data[].bidPx2` | 字符串 | 是 |  |
| `data[].bidPx3` | 字符串 | 是 |  |
| `data[].bidPx4` | 字符串 | 是 |  |
| `data[].bidPx5` | 字符串 | 是 |  |
| `data[].bidVol1` | 整数 | 是 |  |
| `data[].bidVol2` | 整数 | 是 |  |
| `data[].bidVol3` | 整数 | 是 |  |
| `data[].bidVol4` | 整数 | 是 |  |
| `data[].bidVol5` | 整数 | 是 |  |
| `data[].askPx1` | 字符串 | 是 |  |
| `data[].askPx2` | 字符串 | 是 |  |
| `data[].askPx3` | 字符串 | 是 |  |
| `data[].askPx4` | 字符串 | 是 |  |
| `data[].askPx5` | 字符串 | 是 |  |
| `data[].askVol1` | 整数 | 是 |  |
| `data[].askVol2` | 整数 | 是 |  |
| `data[].askVol3` | 整数 | 是 |  |
| `data[].askVol4` | 整数 | 是 |  |
| `data[].askVol5` | 整数 | 是 |  |
| `data[].mktCap` | 实数 | 是 | 总市值。 |
| `data[].floatCap` | 实数 | 是 | 流通规模。 |
| `data[].totShr` | 实数 | 是 | 总份额。 |
| `data[].floatShr` | 实数 | 是 | 流通市值。 |
| `data[].ordImbRatio` | 实数 | 是 | 委比。 |
| `data[].pb` | 整数 | 是 |  |
| `data[].volRatio` | 实数 | 是 | 量比。 |
| `data[].turnover` | 实数 | 是 | 换手率。 |
| `data[].amplitude` | 实数 | 是 | 振幅。 |
| `data[].highLimit` | 实数 | 是 | 涨停价。 |
| `data[].lowLimit` | 实数 | 是 | 跌停价。 |
| `data[].chineseName` | 字符串 | 是 | 中文名称（美股）。 |
| `data[].activeSellVol` | 实数 | 是 | 卖盘。 |
| `data[].activeBuyVol` | 实数 | 是 | 买盘。 |
| `data[].iopv` | 实数 | 是 | iopv(ETF) |

**响应示例**:

```json
{
  "msg": "ok",
  "code": 200,
  "data": [
    {
      "code": "517400",
      "name": "黄金股ETF国泰",
      "type": "FUND",
      "fundType": "ETF",
      "exchangeCode": "XSHG",
      "countryCode": "CHN",
      "timestamp": 1782350197000,
      "localDate": "2026-06-25 09:16:37",
      "price": "1.341",
      "open": "0",
      "high": "0",
      "low": "0",
      "preClose": "1.35",
      "volume": "0",
      "amount": "0",
      "change": "-0.009",
      "changeRate": "-0.67",
      "bidPx1": "1.341",
      "bidPx2": "0",
      "bidPx3": "0",
      "bidPx4": "0",
      "bidPx5": "0",
      "bidVol1": 20400,
      "bidVol2": 298600,
      "bidVol3": 0,
      "bidVol4": 0,
      "bidVol5": 0,
      "askPx1": "1.341",
      "askPx2": "0",
      "askPx3": "0",
      "askPx4": "0",
      "askPx5": "0",
      "askVol1": 20400,
      "askVol2": 0,
      "askVol3": 0,
      "askVol4": 0,
      "askVol5": 0,
      "mktCap": "1107000000",
      "floatCap": "1107000000",
      "totShr": "825792000",
      "floatShr": "825792000",
      "ordImbRatio": -87.98,
      "pb": 0,
      "volRatio": 0,
      "turnover": 0,
      "amplitude": 0,
      "highLimit": "1.485",
      "lowLimit": "1.215"
    },
    {
      "code": "159321",
      "name": "黄金股ETF华安",
      "type": "FUND",
      "fundType": "ETF",
      "exchangeCode": "XSHE",
      "countryCode": "CHN",
      "timestamp": 1782350163000,
      "localDate": "2026-06-25 09:16:03",
      "price": "1.28",
      "open": "0",
      "high": "0",
      "low": "0",
      "preClose": "1.317",
      "volume": "0",
      "amount": "0",
      "change": "-0.037",
      "changeRate": "-2.81",
      "bidPx1": "1.28",
      "bidPx2": "0",
      "bidPx3": "0",
      "bidPx4": "0",
      "bidPx5": "0",
      "bidVol1": 79400,
      "bidVol2": 0,
      "bidVol3": 0,
      "bidVol4": 0,
      "bidVol5": 0,
      "askPx1": "1.28",
      "askPx2": "0",
      "askPx3": "0",
      "askPx4": "0",
      "askPx5": "0",
      "askVol1": 79400,
      "askVol2": 800,
      "askVol3": 0,
      "askVol4": 0,
      "askVol5": 0,
      "mktCap": "488000000",
      "floatCap": "488000000",
      "totShr": "380900397",
      "floatShr": "380900397",
      "ordImbRatio": 0.5,
      "pb": 0,
      "volRatio": 0,
      "turnover": 0,
      "amplitude": 0,
      "highLimit": "1.449",
      "lowLimit": "1.185"
    }
  ]
}
```

---

### <a id="api-17"></a>17. GET 期货列表

| 属性 | 值 |
|------|----|
| **路径** | `/api/future/v1/futureList` |
| **方法** | `GET` |
| **适用版本** | 按量计费、免费版、个人版、专业版、企业版 |

**请求参数**:

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| `token` | query | string | 否 | token,通过登录获取 |
| `countryCode` | query | string (CHN, HKG, USA) | 否 | 国家/地区代码，和交易所二选一。（默认CHN中国大陆，CHN：中国，HKG：中国香港，USA：美国） |
| `exchangeCode` | query | string (ALL, SHFE, INE, DCE, ZCE, CFFEX, GFE, XHKG, CBOT, NYMEX, COMEX, NYBOT) | 否 | 交易所代码，和国家/地区代码二选一。（SHFE：上海期货交易所，INE：上海国际能源交易中心，DCE：大连商品交易所，ZCE：郑州商品交易所，CFFEX：中国金融期货交易所，GFE：广州期货交易所，XHKG：香港期货交易所，CBOT：芝加哥期货交易所，NYMEX：纽约商业交易所  ，COMEX：纽约商品交易所，NYBOT：纽约期货交易所） |

**成功响应 (200)**:

| 字段名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `msg` | 字符串 | 是 | 响应消息 |
| `code` | 字符串 | 是 | 代码 |
| `data` | 数组 | 是 | 响应数据 |
| `data[].code` | 字符串 | 是 | 代码 |
| `data[].name` | 字符串 | 是 | 名称 |
| `data[].type` | 字符串 | 是 | 类型(STOCK：股票，INDEX：指数，FUND：基金，FOREX：外汇，CRYPTO：加密货币) |
| `data[].exchangeCode` | 字符串 | 是 | 交易所代码。详见交易所清单接口。 |
| `data[].countryCode` | 字符串 | 是 | 国家/地区代码。详见国家/地区清单接口。 |
| `data[].chineseName` | 字符串 | 是 | 中文名称（美股）。 |

**响应示例**:

```json
{
  "msg": "ok",
  "code": 200,
  "data": [
    {
      "code": "ad2605",
      "name": "铸造铝2605",
      "type": "FUTURE",
      "exchangeCode": "SHFE",
      "countryCode": "CHN"
    },
    {
      "code": "ao2701",
      "name": "氧化铝2701",
      "type": "FUTURE",
      "exchangeCode": "SHFE",
      "countryCode": "CHN"
    }
  ]
}
```

---

### <a id="api-18"></a>18. GET 期货排行

| 属性 | 值 |
|------|----|
| **路径** | `/api/future/v1/sort` |
| **方法** | `GET` |
| **适用版本** | 按量计费、专业版、企业版 |

**请求参数**:

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| `token` | query | string | 否 | token,通过登录获取 |
| `countryCode` | query | string (CHN, HKG, USA, GBR, MYS, SGP) | 否 | 国家/地区代码，和交易所二选一。（默认CHN中国大陆，CHN：中国，HKG：中国香港，USA：美国，GBR：英国，MYS：马来西亚，SGP：新加坡） |
| `exchangeCode` | query | string (ALL, SHFE, INE, DCE, ZCE, CFFEX, GFE, XHKG, CBOT, NYMEX, COMEX, NYBOT, LME, LCE, SGX, BMD) | 否 | 交易所，和国家/地区二选一。（ALL：所有，SHFE：上海期货交易所，INE：上海国际能源交易中心，DCE：大连商品交易所ZCE：郑州商品交易所，CFFEX：中国金融期货交易所，
                GFE：广州期货交易所，XHKG：香港期货交易所，CBOT：芝加哥期货交易所，NYMEX：纽约商业交易所，COMEX：纽约商品交易所，
                NYBOT：纽约期货交易所，LME：伦敦金属交易所，LCE：伦敦国际金融期货交易所，SGX：新加坡交易所，BMD：马来西亚衍生品交易所） |
| `sort` | query | string (price, change, changeRate, volume, amount, turnover, amplitude, open, high, low, preClose) | 否 | 排序方式。
（price：价格，change：涨跌额，changeRate：涨跌幅，volume：成交量，amount：成交额，turnover：换手率，amplitude：振幅，open：开盘价，high：最高价，low：最低价，preClose：昨收） |
| `order` | query | string (ASC, DESC) | 是 | 顺序：ASC 表升序，DESC 表降序（默认DESC） |
| `page` | query | string | 否 | 第几页，每页100行数据 |

**成功响应 (200)**:

| 字段名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `msg` | 字符串 | 是 | 响应消息 |
| `code` | 字符串 | 是 | 代码 |
| `data` | 对象 | 是 | 响应数据 |
| `data.pageNum` | 整数 | 是 |  |
| `data.pageTotal` | 整数 | 是 |  |
| `data.countTotal` | 整数 | 是 |  |
| `data.list` | 数组 | 是 |  |
| `data.list[].code` | 字符串 | 是 | 代码 |
| `data.list[].name` | 字符串 | 是 | 名称 |
| `data.list[].type` | 字符串 | 是 | 类型(STOCK：股票，INDEX：指数，FUND：基金，FOREX：外汇，CRYPTO：加密货币) |
| `data.list[].exchangeCode` | 字符串 | 是 | 交易所代码。详见交易所清单接口。 |
| `data.list[].countryCode` | 字符串 | 是 | 国家/地区代码。详见国家/地区清单接口。 |
| `data.list[].timestamp` | 整数 | 是 |  |
| `data.list[].localDate` | 字符串 | 是 |  |
| `data.list[].price` | 字符串 | 是 |  |
| `data.list[].open` | 字符串 | 是 |  |
| `data.list[].high` | 字符串 | 是 |  |
| `data.list[].low` | 字符串 | 是 |  |
| `data.list[].preClose` | 字符串 | 是 |  |
| `data.list[].volume` | 字符串 | 是 |  |
| `data.list[].amount` | 字符串 | 是 |  |
| `data.list[].change` | 字符串 | 是 |  |
| `data.list[].changeRate` | 字符串 | 是 |  |
| `data.list[].bidPx1` | 字符串 | 是 |  |
| `data.list[].bidPx2` | 字符串 | 是 |  |
| `data.list[].bidPx3` | 字符串 | 是 |  |
| `data.list[].bidPx4` | 字符串 | 是 |  |
| `data.list[].bidPx5` | 字符串 | 是 |  |
| `data.list[].bidVol1` | 整数 | 是 |  |
| `data.list[].bidVol2` | 整数 | 是 |  |
| `data.list[].bidVol3` | 整数 | 是 |  |
| `data.list[].bidVol4` | 整数 | 是 |  |
| `data.list[].bidVol5` | 整数 | 是 |  |
| `data.list[].askPx1` | 字符串 | 是 |  |
| `data.list[].askPx2` | 字符串 | 是 |  |
| `data.list[].askPx3` | 字符串 | 是 |  |
| `data.list[].askPx4` | 字符串 | 是 |  |
| `data.list[].askPx5` | 字符串 | 是 |  |
| `data.list[].askVol1` | 整数 | 是 |  |
| `data.list[].askVol2` | 整数 | 是 |  |
| `data.list[].askVol3` | 整数 | 是 |  |
| `data.list[].askVol4` | 整数 | 是 |  |
| `data.list[].askVol5` | 整数 | 是 |  |
| `data.list[].activeBuyVol` | 整数 | 是 |  |
| `data.list[].activeSellVol` | 整数 | 是 |  |
| `data.list[].upperPrice` | 字符串 | 是 |  |
| `data.list[].lowerPrice` | 字符串 | 是 |  |
| `data.list[].openInterest` | 整数 | 是 |  |
| `data.list[].preOpenInterest` | 整数 | 是 |  |
| `data.chineseName` | 字符串 | 是 | 中文名称（美股）。 |

**响应示例**:

```json
{
  "msg": "ok",
  "code": 200,
  "data": {
    "pageNum": 1,
    "pageTotal": 26,
    "countTotal": 1258,
    "list": [
      {
        "code": "CF609",
        "name": "棉花609",
        "type": "FUTURE",
        "exchangeCode": "ZCE",
        "countryCode": "CHN",
        "timestamp": 1782350203000,
        "localDate": "2026-06-25 09:16:43",
        "price": "15670",
        "open": "15875",
        "high": "15900",
        "low": "15645",
        "preClose": "15930",
        "volume": "2855930000",
        "amount": "22504728320",
        "change": "-260",
        "changeRate": "-1.63",
        "bidPx1": "15665",
        "bidPx2": "0",
        "bidPx3": "0",
        "bidPx4": "0",
        "bidPx5": "0",
        "bidVol1": 270,
        "bidVol2": 0,
        "bidVol3": 0,
        "bidVol4": 0,
        "bidVol5": 0,
        "askPx1": "0",
        "askPx2": "0",
        "askPx3": "0",
        "askPx4": "0",
        "askPx5": "15670",
        "askVol1": 0,
        "askVol2": 0,
        "askVol3": 0,
        "askVol4": 0,
        "askVol5": 153,
        "activeBuyVol": 117846,
        "activeSellVol": 167747,
        "upperPrice": "16890",
        "lowerPrice": "14970",
        "openInterest": 572162,
        "preOpenInterest": 564431
      },
      {
        "code": "jms",
        "name": "焦煤次主连",
        "type": "FUTURE",
        "exchangeCode": "DCE",
        "countryCode": "CHN",
        "timestamp": 1782350202000,
        "localDate": "2026-06-25 09:16:42",
        "price": "1487",
        "open": "1469",
        "high": "1488",
        "low": "1468",
        "preClose": "1476.5",
        "volume": "187330000",
        "amount": "1663062848",
        "change": "10.5",
        "changeRate": "0.71",
        "bidPx1": "1486.5",
        "bidPx2": "0",
        "bidPx3": "0",
        "bidPx4": "0",
        "bidPx5": "0",
        "bidVol1": 9,
        "bidVol2": 0,
        "bidVol3": 0,
        "bidVol4": 0,
        "bidVol5": 0,
        "askPx1": "0",
        "askPx2": "0",
        "askPx3": "0",
        "askPx4": "0",
        "askPx5": "1487.5",
        "askVol1": 0,
        "askVol2": 0,
        "askVol3": 0,
        "askVol4": 0,
        "askVol5": 20,
        "activeBuyVol": 10306,
        "activeSellVol": 8427,
        "upperPrice": "1594.5",
        "lowerPrice": "1358.5",
        "openInterest": 156076,
        "preOpenInterest": 154473
      }
    ]
  }
}
```

---

### <a id="api-19"></a>19. GET 期货K线

| 属性 | 值 |
|------|----|
| **路径** | `/api/future/v2/kline` |
| **方法** | `GET` |
| **适用版本** | 按量计费、免费版（不含分钟级数据）、个人版（不含分钟级数据）、专业版、企业版 |

**请求参数**:

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| `token` | query | string | 否 | token,通过登录获取 |
| `symbol` | query | string | 否 | 期货代码。 |
| `type` | query | string (day, day5, d1, w1, m1, y1) | 是 | k线类型， day：当日1分钟，day5：最近5个交易日1分钟，d1：日K，w1：周K，m1：月K，y1：年K。 |
| `beginDate` | query | string | 否 | 起始日期。格式“yyyy-mm-dd hh:mm:ss”。 |
| `endDate` | query | string | 否 | 结束日期。格式“yyyy-mm-dd hh:mm:ss”。 |
| `order` | query | string (ASC, DESC) | 否 | 顺序：ASC 表正序，DESC 表倒序（默认在不输入时间为倒序，只输入开始时间为正序，只输入结束时间为倒叙，输入开始时间和结束时间为倒序） |
| `limit` | query | string | 否 | 数量，默认：1000。（最大为2000） |
| `format` | query | string (json, csv) | 否 | 格式,支持json格式和csv格式（默认json格式） |

**成功响应 (200)**:

| 字段名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `msg` | 字符串 | 是 | 响应消息 |
| `code` | 字符串 | 是 | 代码 |
| `data` | 数组 | 是 | 响应数据 |
| `data[].date` | 字符串 | 是 |  |
| `data[].close` | 字符串 | 是 |  |
| `data[].open` | 字符串 | 是 |  |
| `data[].high` | 字符串 | 是 |  |
| `data[].low` | 字符串 | 是 |  |
| `data[].preClose` | 字符串 | 是 |  |
| `data[].volume` | 字符串 | 是 |  |
| `data[].amount` | 字符串 | 是 |  |
| `data[].type` | 字符串 | 是 | 类型(STOCK：股票，INDEX：指数，FUND：基金，FOREX：外汇，CRYPTO：加密货币) |
| `data[].name` | 字符串 | 是 | 名称 |
| `data[].countryCode` | 字符串 | 是 | 国家/地区代码。详见国家/地区清单接口。 |
| `data[].exchangeCode` | 字符串 | 是 | 交易所代码。详见交易所清单接口。 |
| `data[].chineseName` | 字符串 | 是 | 中文名称（美股）。 |

**响应示例**:

```json
{
  "msg": "ok",
  "code": 200,
  "data": [
    {
      "date": "2026-06-25",
      "close": "873.88",
      "open": "877",
      "high": "887.34",
      "low": "868.34",
      "preClose": "896.04",
      "volume": "2426000000",
      "amount": "212913737728"
    },
    {
      "date": "2026-06-24",
      "close": "896.04",
      "open": "898.82",
      "high": "906.48",
      "low": "886.34",
      "preClose": "897.9",
      "volume": "241146",
      "amount": "216342482944"
    }
  ]
}
```

---

### <a id="api-20"></a>20. GET 实时行情

| 属性 | 值 |
|------|----|
| **路径** | `/api/future/v2/realtime` |
| **方法** | `GET` |
| **适用版本** | 按量计费、专业版、企业版 |

**请求参数**:

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| `token` | query | string | 否 | token,通过登录获取 |
| `symbol` | query | string | 否 | 期货代码，支持多个最多一次20个期货数据用英文逗号隔开。 |

**成功响应 (200)**:

| 字段名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `msg` | 字符串 | 是 | 响应消息 |
| `code` | 字符串 | 是 | 代码 |
| `data` | 数组 | 是 | 响应数据 |
| `data[].code` | 字符串 | 是 | 代码 |
| `data[].name` | 字符串 | 是 | 名称 |
| `data[].type` | 字符串 | 是 | 类型(STOCK：股票，INDEX：指数，FUND：基金，FOREX：外汇，CRYPTO：加密货币) |
| `data[].exchangeCode` | 字符串 | 是 | 交易所代码。详见交易所清单接口。 |
| `data[].countryCode` | 字符串 | 是 | 国家/地区代码。详见国家/地区清单接口。 |
| `data[].timestamp` | 整数 | 是 |  |
| `data[].localDate` | 字符串 | 是 |  |
| `data[].price` | 字符串 | 是 |  |
| `data[].open` | 字符串 | 是 |  |
| `data[].high` | 字符串 | 是 |  |
| `data[].low` | 字符串 | 是 |  |
| `data[].preClose` | 字符串 | 是 |  |
| `data[].volume` | 字符串 | 是 |  |
| `data[].amount` | 字符串 | 是 |  |
| `data[].change` | 字符串 | 是 |  |
| `data[].changeRate` | 字符串 | 是 |  |
| `data[].bidPx1` | 字符串 | 是 |  |
| `data[].bidPx2` | 字符串 | 是 |  |
| `data[].bidPx3` | 字符串 | 是 |  |
| `data[].bidPx4` | 字符串 | 是 |  |
| `data[].bidPx5` | 字符串 | 是 |  |
| `data[].bidVol1` | 整数 | 是 |  |
| `data[].bidVol2` | 整数 | 是 |  |
| `data[].bidVol3` | 整数 | 是 |  |
| `data[].bidVol4` | 整数 | 是 |  |
| `data[].bidVol5` | 整数 | 是 |  |
| `data[].askPx1` | 字符串 | 是 |  |
| `data[].askPx2` | 字符串 | 是 |  |
| `data[].askPx3` | 字符串 | 是 |  |
| `data[].askPx4` | 字符串 | 是 |  |
| `data[].askPx5` | 字符串 | 是 |  |
| `data[].askVol1` | 整数 | 是 |  |
| `data[].askVol2` | 整数 | 是 |  |
| `data[].askVol3` | 整数 | 是 |  |
| `data[].askVol4` | 整数 | 是 |  |
| `data[].askVol5` | 整数 | 是 |  |
| `data[].activeBuyVol` | 整数 | 是 |  |
| `data[].activeSellVol` | 整数 | 是 |  |
| `data[].upperPrice` | 字符串 | 是 |  |
| `data[].lowerPrice` | 字符串 | 是 |  |
| `data[].openInterest` | 整数 | 是 |  |
| `data[].preOpenInterest` | 整数 | 是 |  |
| `data[].chineseName` | 字符串 | 是 | 中文名称（美股）。 |

**响应示例**:

```json
{
  "msg": "ok",
  "code": 200,
  "data": [
    {
      "code": "aum",
      "name": "沪金主连",
      "type": "FUTURE",
      "exchangeCode": "SHFE",
      "countryCode": "CHN",
      "timestamp": 1782350203000,
      "localDate": "2026-06-25 09:16:43",
      "price": "873.84",
      "open": "877",
      "high": "887.34",
      "low": "868.34",
      "preClose": "897.14",
      "volume": "2426130000",
      "amount": "212925095936",
      "change": "-23.3",
      "changeRate": "-2.6",
      "bidPx1": "873.68",
      "bidPx2": "873.62",
      "bidPx3": "873.58",
      "bidPx4": "873.56",
      "bidPx5": "873.52",
      "bidVol1": 1,
      "bidVol2": 2,
      "bidVol3": 1,
      "bidVol4": 2,
      "bidVol5": 2,
      "askPx1": "873.94",
      "askPx2": "873.92",
      "askPx3": "873.84",
      "askPx4": "873.82",
      "askPx5": "873.76",
      "askVol1": 1,
      "askVol2": 2,
      "askVol3": 4,
      "askVol4": 3,
      "askVol5": 3,
      "activeBuyVol": 119862,
      "activeSellVol": 122751,
      "upperPrice": "1049.64",
      "lowerPrice": "744.62",
      "openInterest": 159017,
      "preOpenInterest": 159725
    },
    {
      "code": "fum",
      "name": "燃油主连",
      "type": "FUTURE",
      "exchangeCode": "SHFE",
      "countryCode": "CHN",
      "timestamp": 1782350203000,
      "localDate": "2026-06-25 09:16:43",
      "price": "2930",
      "open": "2974",
      "high": "2991",
      "low": "2916",
      "preClose": "3026",
      "volume": "2965900000",
      "amount": "8755539968",
      "change": "-96",
      "changeRate": "-3.17",
      "bidPx1": "2929",
      "bidPx2": "2928",
      "bidPx3": "2927",
      "bidPx4": "2926",
      "bidPx5": "2925",
      "bidVol1": 21,
      "bidVol2": 68,
      "bidVol3": 106,
      "bidVol4": 109,
      "bidVol5": 97,
      "askPx1": "2934",
      "askPx2": "2933",
      "askPx3": "2932",
      "askPx4": "2931",
      "askPx5": "2930",
      "askVol1": 59,
      "askVol2": 51,
      "askVol3": 39,
      "askVol4": 106,
      "askVol5": 34,
      "activeBuyVol": 147422,
      "activeSellVol": 149168,
      "upperPrice": "3540",
      "lowerPrice": "2511",
      "openInterest": 232138,
      "preOpenInterest": 240731
    }
  ]
}
```

---

### <a id="api-21"></a>21. GET 实时行情(返回整个市场实时行情)

| 属性 | 值 |
|------|----|
| **路径** | `/api/future/v2/realtimeMarket` |
| **方法** | `GET` |
| **适用版本** | 企业版 |

**请求参数**:

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| `token` | query | string | 否 | token,通过登录获取 |
| `countryCode` | query | string (CHN, HKG, USA, GBR, MYS, SGP) | 否 | 国家/地区代码，和交易所二选一。（默认CHN中国大陆，CHN：中国，HKG：中国香港，USA：美国，GBR：英国，MYS：马来西亚，SGP：新加坡） |
| `exchangeCode` | query | string (ALL, SHFE, INE, DCE, ZCE, CFFEX, GFE, XHKG, CBOT, NYMEX, COMEX, NYBOT, LME, LCE, SGX, BMD) | 否 | 交易所代码，和国家/地区代码二选一。（SHFE：上海期货交易所，INE：上海国际能源交易中心，DCE：大连商品交易所，ZCE：郑州商品交易所，CFFEX：中国金融期货交易所，GFE：广州期货交易所，XHKG：香港期货交易所，CBOT：芝加哥期货交易所，NYMEX：纽约商业交易所  ，COMEX：纽约商品交易所，NYBOT：纽约期货交易所，LME：伦敦金属交易所，LCE：伦敦国际金融期货交易所，SGX：新加坡交易所BMD：马来西亚衍生品交易所） |
| `fields` | query | string | 否 | 返回的字段，中间以逗号分隔，字段名称点击”响应Response“可查看，输入all默认返回所有数据。 |
| `format` | query | string (json, csv) | 否 | 格式,支持json格式和csv格式（默认json格式） |

**成功响应 (200)**:

| 字段名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `msg` | 字符串 | 是 | 响应消息 |
| `code` | 字符串 | 是 | 代码 |
| `data` | 数组 | 是 | 响应数据 |
| `data[].code` | 字符串 | 是 | 代码 |
| `data[].exchangeCode` | 字符串 | 是 | 交易所代码。详见交易所清单接口。 |
| `data[].high` | 字符串 | 是 | 最高价 |
| `data[].low` | 字符串 | 是 | 最低价 |
| `data[].name` | 字符串 | 是 | 名称 |
| `data[].open` | 字符串 | 是 | 开盘价 |
| `data[].preClose` | 字符串 | 是 | 收盘价 |
| `data[].price` | 字符串 | 是 | 价格 |
| `data[].type` | 字符串 | 是 | 类型(future：股票，INDEX：指数，FUND：基金，FOREX：外汇，CRYPTO：加密货币) |
| `data[].countryCode` | 字符串 | 是 | 国家/地区代码。详见国家/地区清单接口。 |
| `data[].chineseName` | 字符串 | 是 | 中文名称（美股）。 |
| `data[].localDate` | 字符串 | 是 | 更新时间。 |
| `data[].volume` | 字符串 | 是 | 成交量 |
| `data[].amount` | 字符串 | 是 | 成交额 |
| `data[].change` | 字符串 | 是 | 涨跌额 |
| `data[].changeRate` | 字符串 | 是 | 涨跌幅 |
| `data[].activeSellVol` | 整数 | 是 | 内盘(主动卖出总量) |
| `data[].activeBuyVol` | 整数 | 是 | 外盘(主动买入总量) |
| `data[].floatCap` | 字符串 | 是 | 流通市值 |
| `data[].mktCap` | 字符串 | 是 | 总市值 |
| `data[].floatShr` | 字符串 | 是 | 流通股本 |
| `data[].totShr` | 字符串 | 是 | 总股本 |
| `data[].ordImbRatio` | 字符串 | 是 | 委比 |
| `data[].pb` | 字符串 | 是 | 市净率 |
| `data[].turnover` | 字符串 | 是 | 换手率 |
| `data[].pe_ttm` | 字符串 | 是 | TTM市盈率 |
| `data[].pe_dyn` | 字符串 | 是 | 动态市盈率 |
| `data[].pe_static` | 字符串 | 是 | 静态市盈率 |
| `data[].amplitude` | 字符串 | 是 | 振幅 |
| `data[].highLimit` | 字符串 | 是 | 涨停价格 |
| `data[].lowLimit` | 字符串 | 是 | 跌停价格 |
| `data[].askPx1` | 实数 | 是 | 卖一价 |
| `data[].askVol1` | 整数 | 是 | 卖一量 |
| `data[].askPx2` | 实数 | 是 | 卖二价 |
| `data[].askVol2` | 整数 | 是 | 卖二量 |
| `data[].askPx3` | 实数 | 是 | 卖三价 |
| `data[].askVol3` | 整数 | 是 | 卖三量 |
| `data[].askPx4` | 实数 | 是 | 卖四价 |
| `data[].askVol4` | 整数 | 是 | 卖四量 |
| `data[].askPx5` | 实数 | 是 | 卖五价 |
| `data[].askVol5` | 整数 | 是 | 卖五量 |
| `data[].bidPx1` | 实数 | 是 | 买一价 |
| `data[].bidVol1` | 整数 | 是 | 买一量 |
| `data[].bidPx2` | 实数 | 是 | 买二价 |
| `data[].bidVol2` | 整数 | 是 | 买二量 |
| `data[].bidPx3` | 实数 | 是 | 买三价 |
| `data[].bidVol3` | 整数 | 是 | 买三量 |
| `data[].bidPx4` | 实数 | 是 | 买四价 |
| `data[].bidVol4` | 整数 | 是 | 买四量 |
| `data[].bidPx5` | 实数 | 是 | 买五价 |
| `data[].bidVol5` | 整数 | 是 | 买五量 |

**响应示例**:

```json
{
  "msg": "ok",
  "code": 200,
  "data": [
    {
      "code": "is",
      "exchangeCode": "DCE",
      "high": "737",
      "low": "733",
      "name": "铁矿石次主连",
      "open": "734.5",
      "preClose": "732.5",
      "price": "734.5"
    },
    {
      "code": "PL612",
      "exchangeCode": "ZCE",
      "high": "6533",
      "low": "6420",
      "name": "丙烯612",
      "open": "6453",
      "preClose": "6584",
      "price": "6533"
    }
  ]
}
```

---

### <a id="api-22"></a>22. GET 指数成分股列表

| 属性 | 值 |
|------|----|
| **路径** | `/api/index/v1/constituent` |
| **方法** | `GET` |
| **适用版本** | 按量计费、免费版、个人版、专业版、企业版 |

**请求参数**:

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| `token` | query | string | 否 | token,通过登录获取 |
| `symbol` | query | string | 是 | 指数代码。（上证用sh开头，深证用sz开头，北证用bj开头，港股用hk开头，美股用us开头） |

**成功响应 (200)**:

| 字段名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `msg` | 字符串 | 是 | 响应消息 |
| `code` | 字符串 | 是 | 代码 |
| `data` | 数组 | 是 | 响应数据 |
| `data[].code` | 字符串 | 是 | 代码 |
| `data[].name` | 字符串 | 是 | 名称 |
| `data[].type` | 字符串 | 是 | 类型(STOCK：股票，INDEX：指数，FUND：基金，FOREX：外汇，CRYPTO：加密货币) |
| `data[].exchangeCode` | 字符串 | 是 | 交易所代码。详见交易所清单接口。 |
| `data[].countryCode` | 字符串 | 是 | 国家/地区代码。详见国家/地区清单接口。 |
| `data[].chineseName` | 字符串 | 是 | 中文名称（美股）。 |

**响应示例**:

```json
{
  "msg": "ok",
  "code": 200,
  "data": [
    {
      "code": "688008",
      "name": "澜起科技",
      "type": "STOCK",
      "exchangeCode": "XSHG",
      "countryCode": "CHN"
    },
    {
      "code": "688702",
      "name": "盛科通信-U",
      "type": "STOCK",
      "exchangeCode": "XSHG",
      "countryCode": "CHN"
    }
  ]
}
```

---

### <a id="api-23"></a>23. GET 指数列表

| 属性 | 值 |
|------|----|
| **路径** | `/api/index/v1/indexList` |
| **方法** | `GET` |
| **适用版本** | 按量计费、免费版、个人版、专业版、企业版 |

**请求参数**:

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| `token` | query | string | 否 | token,通过登录获取 |
| `countryCode` | query | string (CHN, HKG, USA) | 否 | 国家/地区代码，和交易所，股票市场三选一。（CHN：中国大陆，HKG：中国香港，USA：美国）） |
| `format` | query | string (json, csv) | 否 | 格式,支持json格式和csv格式（默认json格式） |

**成功响应 (200)**:

| 字段名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `msg` | 字符串 | 是 | 响应消息 |
| `code` | 字符串 | 是 | 代码 |
| `data` | 数组 | 是 | 响应数据 |
| `data[].code` | 字符串 | 是 | 代码 |
| `data[].name` | 字符串 | 是 | 名称 |
| `data[].type` | 字符串 | 是 | 类型(STOCK：股票，INDEX：指数，FUND：基金，FOREX：外汇，CRYPTO：加密货币) |
| `data[].exchangeCode` | 字符串 | 是 | 交易所代码。详见交易所清单接口。 |
| `data[].countryCode` | 字符串 | 是 | 国家/地区代码。详见国家/地区清单接口。 |
| `data[].chineseName` | 字符串 | 是 | 中文名称（美股）。 |

**响应示例**:

```json
{
  "msg": "ok",
  "code": 200,
  "data": [
    {
      "code": "000009",
      "name": "上证380",
      "type": "INDEX",
      "exchangeCode": "XSHG",
      "countryCode": "CHN"
    },
    {
      "code": "000860",
      "name": "结构调整",
      "type": "INDEX",
      "exchangeCode": "XSHG",
      "countryCode": "CHN"
    }
  ]
}
```

---

### <a id="api-24"></a>24. GET 实时行情(返回整个市场实时行情)

| 属性 | 值 |
|------|----|
| **路径** | `/api/index/v1/realtimeMarket` |
| **方法** | `GET` |
| **适用版本** | 企业版 |

**请求参数**:

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| `token` | query | string | 否 | token,通过登录获取 |
| `countryCode` | query | string (CHN, HKG, USA) | 否 | 国家/地区代码，默认CHN。（CHN：中国大陆）） |
| `fields` | query | string | 否 | 返回的字段，中间以逗号分隔，字段名称点击”响应Response“可查看，输入all默认返回所有数据。 |
| `format` | query | string (json, csv) | 否 | 格式,支持json格式和csv格式（默认json格式） |

**成功响应 (200)**:

| 字段名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `msg` | 字符串 | 是 | 响应消息 |
| `code` | 字符串 | 是 | 代码 |
| `data` | 数组 | 是 | 响应数据 |
| `data[].code` | 字符串 | 是 | 代码 |
| `data[].exchangeCode` | 字符串 | 是 | 交易所代码。详见交易所清单接口。 |
| `data[].high` | 实数 | 是 | 最高价 |
| `data[].low` | 实数 | 是 | 最低价 |
| `data[].name` | 字符串 | 是 | 名称 |
| `data[].open` | 实数 | 是 | 开盘价 |
| `data[].preClose` | 实数 | 是 | 昨收 |
| `data[].price` | 实数 | 是 | 价格 |
| `data[].type` | 字符串 | 是 | 类型(STOCK：股票，INDEX：指数，FUND：基金，FOREX：外汇，CRYPTO：加密货币) |
| `data[].countryCode` | 字符串 | 是 | 国家/地区代码。详见国家/地区清单接口。 |
| `data[].chineseName` | 字符串 | 是 | 中文名称（美股）。 |
| `data[].localDate` | 字符串 | 是 | 时间 |
| `data[].change` | 实数 | 是 | 涨跌额 |
| `data[].changeRate` | 实数 | 是 | 涨跌幅 |
| `data[].amplitude` | 实数 | 是 | 振幅 |
| `data[].volume` | 整数 | 是 | 成交量 |
| `data[].amount` | 实数 | 是 | 成交额 |
| `data[].ordImbRatio` | 实数 | 是 | 委比 |
| `data[].floatCap` | 实数 | 是 | 流通市值 |
| `data[].mktCap` | 实数 | 是 | 总市值 |
| `data[].turnover` | 实数 | 是 | 换手率 |
| `data[].volRatio` | 实数 | 是 | 量比 |

**响应示例**:

```json
{
  "msg": "ok",
  "code": 200,
  "data": [
    {
      "code": "000009",
      "exchangeCode": "XSHG",
      "high": "0",
      "low": "0",
      "name": "上证380",
      "open": "0",
      "preClose": "7486.14",
      "price": "7484.7"
    },
    {
      "code": "000860",
      "exchangeCode": "XSHG",
      "high": "0",
      "low": "0",
      "name": "结构调整",
      "open": "0",
      "preClose": "1320.2",
      "price": "1319.11"
    }
  ]
}
```

---

### <a id="api-25"></a>25. GET 指数排序

| 属性 | 值 |
|------|----|
| **路径** | `/api/index/v1/sort` |
| **方法** | `GET` |
| **适用版本** | 按量计费、专业版、企业版 |

**请求参数**:

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| `token` | query | string | 否 | token,通过登录获取 |
| `countryCode` | query | string (CHN, HKG, USA) | 否 | 国家/地区代码，和交易所，股票市场三选一。（CHN：中国大陆，HKG：中国香港，USA：美国）） |
| `sort` | query | string (price, change, changeRate, volume, amount, turnover, committee, circulationValue, marketValue, circulationShares, totalShares, amplitude, open, high, low, preClose) | 否 | 排序方式。
（price：价格，change：涨跌额，changeRate：涨跌幅，volume：成交量，amount：成交额，turnover：换手率，committee：委比，circulationValue：流通市值，marketValue：总市值，amplitude：振幅，open：开盘价，high：最高价，low：最低价，preClose：昨收） |
| `order` | query | string (ASC, DESC) | 是 | 顺序：ASC 表升序，DESC 表降序（默认DESC） |
| `page` | query | string | 否 | 第几页，每页100行数据 |

**成功响应 (200)**:

| 字段名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `msg` | 字符串 | 是 | 响应消息 |
| `code` | 字符串 | 是 | 代码 |
| `data` | 对象 | 是 | 响应数据 |
| `data.pageNum` | 整数 | 是 |  |
| `data.pageTotal` | 整数 | 是 |  |
| `data.countTotal` | 整数 | 是 |  |
| `data.list` | 数组 | 是 |  |
| `data.list[].code` | 字符串 | 是 | 代码 |
| `data.list[].name` | 字符串 | 是 | 名称 |
| `data.list[].type` | 字符串 | 是 | 类型(STOCK：股票，INDEX：指数，FUND：基金，FOREX：外汇，CRYPTO：加密货币) |
| `data.list[].exchangeCode` | 字符串 | 是 | 交易所代码。详见交易所清单接口。 |
| `data.list[].countryCode` | 字符串 | 是 | 国家/地区代码。详见国家/地区清单接口。 |
| `data.list[].timestamp` | 整数 | 是 |  |
| `data.list[].localDate` | 字符串 | 是 | 时间 |
| `data.list[].price` | 实数 | 是 | 价格 |
| `data.list[].open` | 实数 | 是 | 开盘价 |
| `data.list[].high` | 实数 | 是 | 最高价 |
| `data.list[].low` | 实数 | 是 | 最低价 |
| `data.list[].preClose` | 实数 | 是 | 昨收 |
| `data.list[].volume` | 整数 | 是 | 成交量 |
| `data.list[].amount` | 实数 | 是 | 成交额 |
| `data.list[].change` | 实数 | 是 | 涨跌额 |
| `data.list[].changeRate` | 实数 | 是 | 涨跌幅 |
| `data.list[].mktCap` | 实数 | 是 | 总市值 |
| `data.list[].floatCap` | 实数 | 是 | 流通市值 |
| `data.list[].volRatio` | 实数 | 是 | 量比 |
| `data.list[].pe_ttm` | 整数 | 是 |  |
| `data.list[].amplitude` | 实数 | 是 | 振幅 |
| `data.chineseName` | 字符串 | 是 | 中文名称（美股）。 |
| `data.ordImbRatio` | 实数 | 是 | 委比 |
| `data.turnover` | 实数 | 是 | 换手率 |

**响应示例**:

```json
{
  "msg": "ok",
  "code": 200,
  "data": {
    "pageNum": 1,
    "pageTotal": 12,
    "countTotal": 562,
    "list": [
      {
        "code": "000170",
        "name": "50AH优选",
        "type": "INDEX",
        "exchangeCode": "XSHG",
        "countryCode": "CHN",
        "timestamp": 1782350179000,
        "localDate": "2026-06-25 09:16:19",
        "price": "6107.07",
        "open": "0",
        "high": "0",
        "low": "0",
        "preClose": "6104.29",
        "volume": "1302000",
        "amount": "25020000",
        "change": "2.78",
        "changeRate": "0.05",
        "mktCap": "9456297000000",
        "floatCap": "9247465000000",
        "volRatio": 0,
        "pe_ttm": 19,
        "amplitude": 0
      },
      {
        "code": "000061",
        "name": "沪企债30",
        "type": "INDEX",
        "exchangeCode": "XSHG",
        "countryCode": "CHN",
        "timestamp": 1782350163000,
        "localDate": "2026-06-25 09:16:03",
        "price": "181.56",
        "open": "0",
        "high": "0",
        "low": "0",
        "preClose": "181.55",
        "volume": "0",
        "amount": "0",
        "change": "0.01",
        "changeRate": "0.01",
        "volRatio": 0,
        "amplitude": 0
      }
    ]
  }
}
```

---

### <a id="api-26"></a>26. GET 指数K线

| 属性 | 值 |
|------|----|
| **路径** | `/api/index/v2/kline` |
| **方法** | `GET` |
| **适用版本** | 按量计费、免费版（不含分钟级数据）、个人版（不含分钟级数据）、专业版、企业版 |

**请求参数**:

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| `token` | query | string | 否 | token,通过登录获取 |
| `symbol` | query | string | 是 | 指数代码，上证用sh开头，深证用sz开头，北证用bj开头，港股用hk开头，美股用us开头。 |
| `type` | query | string (day, day5, d1, w1, m1, y1) | 是 | k线类型， day：当日1分钟，day5：最近5个交易日1分钟，d1：日K，w1：周K，m1：月K，y1：年K。 |
| `beginDate` | query | string | 否 | 起始日期。格式“yyyy-mm-dd hh:mm:ss”。 |
| `endDate` | query | string | 否 | 结束日期。格式“yyyy-mm-dd hh:mm:ss”。 |
| `order` | query | string (ASC, DESC) | 否 | 顺序：ASC 表正序，DESC 表倒序（默认在不输入时间为倒序，只输入开始时间为正序，只输入结束时间为倒叙，输入开始时间和结束时间为倒序） |
| `limit` | query | string | 否 | 数量，默认：1000。（最大为2000） |
| `fq` | query | string (bfq, qfq) | 否 | 复权：默认不复权。（bfq 表不复权，qfq 表示前复权） |
| `format` | query | string (json, csv) | 否 | 格式,支持json格式和csv格式（默认json格式） |

**成功响应 (200)**:

| 字段名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `msg` | 字符串 | 是 | 响应消息 |
| `code` | 字符串 | 是 | 代码 |
| `data` | 数组 | 是 | 响应数据 |
| `data[].date` | 字符串 | 是 | 更新时间 |
| `data[].close` | 字符串 | 是 | 收盘价 |
| `data[].open` | 字符串 | 是 | 开盘价格 |
| `data[].high` | 字符串 | 是 | 最高价 |
| `data[].low` | 字符串 | 是 | 最低价 |
| `data[].preClose` | 字符串 | 是 | 昨收 |
| `data[].volume` | 字符串 | 是 | 成交量 |
| `data[].amount` | 字符串 | 是 | 成交额 |
| `data[].time` | 整数 | 是 | 时间戳(毫秒) |

**响应示例**:

```json
{
  "msg": "ok",
  "code": 200,
  "data": [
    {
      "date": "2026-06-25",
      "close": "4110.16",
      "open": "0",
      "high": "0",
      "low": "0",
      "preClose": "4110.81",
      "volume": "0",
      "amount": "0"
    },
    {
      "date": "2026-06-24",
      "close": "4110.81",
      "open": "4090.1",
      "high": "4117.28",
      "low": "4075.49",
      "preClose": "4106.25",
      "volume": "64452751800",
      "amount": "1514193285000"
    }
  ]
}
```

---

### <a id="api-27"></a>27. GET 实时行情

| 属性 | 值 |
|------|----|
| **路径** | `/api/index/v2/realtime` |
| **方法** | `GET` |
| **适用版本** | 按量计费、专业版、企业版 |

**请求参数**:

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| `token` | query | string | 否 | token,通过登录获取 |
| `symbol` | query | string | 是 | 股票代码，支持多个最多一次20个指数数据用英文逗号隔开，（上证用开头，深证用sz开头，北证用bj开头，港股用hk开头，美股用us开头）。 |
| `format` | query | string (json, csv) | 否 | 格式,支持json格式和csv格式（默认json格式） |

**成功响应 (200)**:

| 字段名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `msg` | 字符串 | 是 | 响应消息 |
| `code` | 字符串 | 是 | 代码 |
| `data` | 数组 | 是 | 响应数据 |
| `data[].code` | 字符串 | 是 | 代码 |
| `data[].name` | 字符串 | 是 | 名称 |
| `data[].type` | 字符串 | 是 | 类型(STOCK：股票，INDEX：指数，FUND：基金，FOREX：外汇，CRYPTO：加密货币) |
| `data[].exchangeCode` | 字符串 | 是 | 交易所代码。详见交易所清单接口。 |
| `data[].countryCode` | 字符串 | 是 | 国家/地区代码。详见国家/地区清单接口。 |
| `data[].timestamp` | 整数 | 是 |  |
| `data[].localDate` | 字符串 | 是 | 时间 |
| `data[].price` | 实数 | 是 | 价格 |
| `data[].open` | 实数 | 是 | 开盘价 |
| `data[].high` | 实数 | 是 | 最高价 |
| `data[].low` | 实数 | 是 | 最低价 |
| `data[].preClose` | 实数 | 是 | 昨收 |
| `data[].volume` | 整数 | 是 | 成交量 |
| `data[].amount` | 实数 | 是 | 成交额 |
| `data[].change` | 实数 | 是 | 涨跌额 |
| `data[].changeRate` | 实数 | 是 | 涨跌幅 |
| `data[].mktCap` | 实数 | 是 | 总市值 |
| `data[].floatCap` | 实数 | 是 | 流通市值 |
| `data[].volRatio` | 实数 | 是 | 量比 |
| `data[].pe_ttm` | 实数 | 是 |  |
| `data[].amplitude` | 实数 | 是 | 振幅 |
| `data[].chineseName` | 字符串 | 是 | 中文名称（美股）。 |
| `data[].ordImbRatio` | 实数 | 是 | 委比 |
| `data[].turnover` | 实数 | 是 | 换手率 |

**响应示例**:

```json
{
  "msg": "ok",
  "code": 200,
  "data": [
    {
      "code": "000001",
      "name": "上证指数",
      "type": "INDEX",
      "exchangeCode": "XSHG",
      "countryCode": "CHN",
      "timestamp": 1782350163000,
      "localDate": "2026-06-25 09:16:03",
      "price": "4110.16",
      "open": "0",
      "high": "0",
      "low": "0",
      "preClose": "4110.81",
      "volume": "0",
      "amount": "0",
      "change": "-0.65",
      "changeRate": "-0.02",
      "mktCap": "68980027000000",
      "floatCap": "63657581000000.01",
      "volRatio": 0,
      "pe_ttm": 18.11,
      "amplitude": 0
    },
    {
      "code": "399001",
      "name": "深证成指",
      "type": "INDEX",
      "exchangeCode": "XSHE",
      "countryCode": "CHN",
      "timestamp": 1782350181000,
      "localDate": "2026-06-25 09:16:21",
      "price": "16051.32",
      "open": "0",
      "high": "0",
      "low": "0",
      "preClose": "16051.32",
      "volume": "0",
      "amount": "0",
      "change": "0",
      "changeRate": "0",
      "mktCap": "49659357000000",
      "floatCap": "42438702000000",
      "volRatio": 0,
      "pe_ttm": 52.58,
      "amplitude": 0
    }
  ]
}
```

---

### <a id="api-28"></a>28. GET 贵金属列表

| 属性 | 值 |
|------|----|
| **路径** | `/api/metal/v1/metalList` |
| **方法** | `GET` |
| **适用版本** | 按量计费、免费版、个人版、专业版、企业版 |

**请求参数**:

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| `token` | query | string | 否 | token,通过登录获取 |
| `exchangeCode` | query | string (SGE) | 否 | 交易所代码，默认SGE。（SGE：上海黄金交易所） |

**成功响应 (200)**:

| 字段名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `msg` | 字符串 | 是 | 响应消息 |
| `code` | 字符串 | 是 | 代码 |
| `data` | 数组 | 是 | 响应数据 |
| `data[].code` | 字符串 | 是 | 代码 |
| `data[].name` | 字符串 | 是 | 名称 |
| `data[].chineseName` | 字符串 | 是 |  |
| `data[].type` | 字符串 | 是 | 类型(METAL：贵金属) |
| `data[].exchangeCode` | 字符串 | 是 | 交易所代码 |
| `data[].countryCode` | 字符串 | 是 | 国家/地区代码 |

**响应示例**:

```json
{
  "msg": "ok",
  "code": 200,
  "data": [
    {
      "code": "iAu99.99",
      "name": "国际板黄金9999",
      "chineseName": "国际板黄金9999",
      "type": "METAL",
      "exchangeCode": "SGE",
      "countryCode": "CHN"
    },
    {
      "code": "Au99.99",
      "name": "黄金9999",
      "chineseName": "黄金9999",
      "type": "METAL",
      "exchangeCode": "SGE",
      "countryCode": "CHN"
    }
  ]
}
```

---

### <a id="api-29"></a>29. GET 贵金属排行

| 属性 | 值 |
|------|----|
| **路径** | `/api/metal/v1/sort` |
| **方法** | `GET` |
| **适用版本** | 专业版、企业版 |

**请求参数**:

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| `token` | query | string | 否 | token,通过登录获取 |
| `exchangeCode` | query | string (SGE) | 否 | 交易所代码，默认SGE。 |
| `sort` | query | string (price, change, changeRate, volume, amount) | 是 | 排序字段。 |
| `order` | query | string (asc, desc) | 否 | 排序方向，asc或desc。 |
| `page` | query | string | 否 | 页码。 |

**成功响应 (200)**:

| 字段名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `msg` | 字符串 | 是 | 响应消息 |
| `code` | 整数 | 是 | 响应状态码，200 表示成功 |
| `data` | 对象 | 是 | 响应数据 |
| `data.pageNum` | 整数 | 是 | 当前页 |
| `data.pageTotal` | 整数 | 是 | 总页数 |
| `data.countTotal` | 整数 | 是 | 总数量 |
| `data.list` | 数组 | 是 | 排行数据 |

**响应示例**:

```json
{
  "msg": "ok",
  "code": 200,
  "data": {
    "pageNum": 1,
    "pageTotal": 1,
    "countTotal": 0,
    "list": null
  }
}
```

---

### <a id="api-30"></a>30. GET 贵金属K线

| 属性 | 值 |
|------|----|
| **路径** | `/api/metal/v2/kline` |
| **方法** | `GET` |
| **适用版本** | 按量计费、免费版、个人版、专业版、企业版 |

**请求参数**:

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| `token` | query | string | 否 | token,通过登录获取 |
| `symbol` | query | string | 是 | 贵金属代码。 |
| `type` | query | string (d1, w1, m1, y1) | 是 | K线类型，d1：日K，w1：周K，m1：月K，y1：年K。 |
| `beginDate` | query | string | 否 | 起始日期。格式“yyyy-mm-dd hh:mm:ss”。 |
| `endDate` | query | string | 否 | 结束日期。格式“yyyy-mm-dd hh:mm:ss”。 |
| `format` | query | string (json, csv) | 否 | 格式,支持json格式和csv格式（默认json格式） |

**成功响应 (200)**:

| 字段名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `msg` | 字符串 | 是 | 响应消息 |
| `code` | 整数 | 是 | 响应状态码，200 表示成功 |
| `data` | 数组 | 是 | 响应数据 |
| `data[].date` | 字符串 | 是 | 交易日 |
| `data[].open` | 浮点数 | 是 | 开盘价 |
| `data[].high` | 浮点数 | 是 | 最高价 |
| `data[].low` | 浮点数 | 是 | 最低价 |
| `data[].close` | 浮点数 | 是 | 收盘价 |

**响应示例**:

```json
{
  "msg": "ok",
  "code": 200,
  "data": []
}
```

---

### <a id="api-31"></a>31. GET 贵金属实时行情

| 属性 | 值 |
|------|----|
| **路径** | `/api/metal/v2/realtime` |
| **方法** | `GET` |
| **适用版本** | 专业版、企业版 |

**请求参数**:

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| `token` | query | string | 否 | token,通过登录获取 |
| `symbol` | query | string | 是 | 贵金属代码，多个代码用英文逗号分隔。 |
| `format` | query | string (json, csv) | 否 | 格式,支持json格式和csv格式（默认json格式） |

**成功响应 (200)**:

| 字段名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `msg` | 字符串 | 是 | 响应消息 |
| `code` | 字符串 | 是 | 代码 |
| `data` | 数组 | 是 | 响应数据 |
| `data[].type` | 字符串 | 是 | 类型(METAL：贵金属) |
| `data[].price` | 浮点数 | 是 | 最新价 |

**响应示例**:

```json
{
  "msg": "ok",
  "code": 200,
  "data": []
}
```

---

### <a id="api-32"></a>32. GET 贵金属实时行情(整个市场)

| 属性 | 值 |
|------|----|
| **路径** | `/api/metal/v2/realtimeMarket` |
| **方法** | `GET` |
| **适用版本** | 企业版 |

**请求参数**:

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| `token` | query | string | 否 | token,通过登录获取 |
| `exchangeCode` | query | string (SGE) | 否 | 交易所代码，默认SGE。 |
| `fields` | query | string | 否 | 返回字段，多个字段用英文逗号分隔，all表示全部字段。 |
| `format` | query | string (json, csv) | 否 | 格式,支持json格式和csv格式（默认json格式） |

**成功响应 (200)**:

| 字段名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `msg` | 字符串 | 是 | 响应消息 |
| `code` | 字符串 | 是 | 代码 |
| `data` | 数组 | 是 | 响应数据 |
| `data[].type` | 字符串 | 是 | 类型(METAL：贵金属) |
| `data[].price` | 浮点数 | 是 | 最新价 |

**响应示例**:

```json
{
  "msg": "ok",
  "code": 200,
  "data": []
}
```

---

### <a id="api-33"></a>33. GET 板块成分股

| 属性 | 值 |
|------|----|
| **路径** | `/api/sector/v1/constituent` |
| **方法** | `GET` |
| **适用版本** | 按量计费、免费版、个人版、专业版、企业版 |

**请求参数**:

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| `token` | query | string | 否 | token,通过登录获取 |
| `symbol` | query | string | 是 | 板块代码。（中国大陆可用cn开头，不加来源默认EM，也支持代码加来源后缀） |

**成功响应 (200)**:

| 字段名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `msg` | 字符串 | 是 | 响应消息 |
| `code` | 字符串 | 是 | 代码 |
| `data` | 数组 | 是 | 响应数据 |
| `data[].code` | 字符串 | 是 | 代码 |
| `data[].name` | 字符串 | 是 | 名称 |
| `data[].type` | 字符串 | 是 | 类型(STOCK：股票，INDEX：指数，FUND：基金，FOREX：外汇，CRYPTO：加密货币) |
| `data[].exchangeCode` | 字符串 | 是 | 交易所代码。详见交易所清单接口。 |
| `data[].countryCode` | 字符串 | 是 | 国家/地区代码。详见国家/地区清单接口。 |
| `data[].chineseName` | 字符串 | 是 | 中文名称（美股）。 |

**响应示例**:

```json
{
  "msg": "ok",
  "code": 200,
  "data": [
    {
      "code": "603375",
      "name": "盛景微",
      "type": "STOCK",
      "exchangeCode": "XSHG",
      "countryCode": "CHN"
    },
    {
      "code": "688699",
      "name": "明微电子",
      "type": "STOCK",
      "exchangeCode": "XSHG",
      "countryCode": "CHN"
    }
  ]
}
```

---

### <a id="api-34"></a>34. GET 实时行情(返回整个市场实时行情)

| 属性 | 值 |
|------|----|
| **路径** | `/api/sector/v1/realtimeMarket` |
| **方法** | `GET` |
| **适用版本** | 企业版 |

**请求参数**:

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| `token` | query | string | 否 | token,通过登录获取 |
| `countryCode` | query | string (CHN) | 否 | 国家/地区代码，默认CHN。（CHN：中国大陆）） |
| `exchangeCode` | query | string (EM) | 否 | 来源代码，默认EM。（EM：东方财富） |
| `sectorType` | query | string (all, industry, concept, region) | 否 | 类型。（all：所有，industry：行业，concept：概念，region：区域 |
| `fields` | query | string | 否 | 返回的字段，中间以逗号分隔，字段名称点击”响应Response“可查看，输入all默认返回所有数据。 |
| `format` | query | string (json, csv) | 否 | 格式,支持json格式和csv格式（默认json格式） |

**成功响应 (200)**:

| 字段名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `msg` | 字符串 | 是 | 响应消息 |
| `code` | 字符串 | 是 | 代码 |
| `data` | 数组 | 是 | 响应数据 |
| `data[].code` | 字符串 | 是 | 代码 |
| `data[].exchangeCode` | 字符串 | 是 | 来源代码。详见交易所清单接口。 |
| `data[].high` | 实数 | 是 | 最高价 |
| `data[].low` | 实数 | 是 | 最低价 |
| `data[].name` | 字符串 | 是 | 名称 |
| `data[].open` | 实数 | 是 | 开盘价 |
| `data[].preClose` | 实数 | 是 | 昨收 |
| `data[].price` | 实数 | 是 | 价格 |
| `data[].type` | 字符串 | 是 | 类型(STOCK：股票，INDEX：指数，FUND：基金，FOREX：外汇，CRYPTO：加密货币) |
| `data[].countryCode` | 字符串 | 是 | 国家/地区代码。详见国家/地区清单接口。 |
| `data[].sectorType` | 字符串 | 是 | 板块类型（Industry：行业板块，Concept：概念板块，Region：地域板块）。 |
| `data[].localDate` | 字符串 | 是 | 时间 |
| `data[].volume` | 整数 | 是 | 成交量 |
| `data[].amount` | 实数 | 是 | 成交额 |
| `data[].mktCap` | 实数 | 是 | 总市值 |
| `data[].floatCap` | 实数 | 是 | 流通市值 |
| `data[].totShr` | 实数 | 是 | 总股本 |
| `data[].floatShr` | 实数 | 是 | 流通股本 |
| `data[].change` | 实数 | 是 | 涨跌额 |
| `data[].changeRate` | 实数 | 是 | 涨跌幅 |
| `data[].amplitude` | 实数 | 是 | 振幅 |
| `data[].ordImbRatio` | 实数 | 是 | 委比 |
| `data[].turnover` | 实数 | 是 | 换手率 |
| `data[].volRatio` | 实数 | 是 | 量比 |
| `data[].activeSellVol` | 整数 | 是 | 内盘(主动卖出总量) |
| `data[].activeBuyVol` | 整数 | 是 | 外盘(主动买入总量) |
| `data[].netInflow` | 实数 | 是 | 净流入 |
| `data[].riseCount` | 整数 | 是 | 上涨股票数量 |
| `data[].fallCount` | 整数 | 是 | 下跌股票数量 |
| `data[].flatCount` | 整数 | 是 | 持平股票数量 |
| `data[].riseFirstStock` | 对象 | 是 | 涨幅最大的股票 |
| `data[].fallFirstStock` | 对象 | 是 | 跌幅最大的股票 |

**响应示例**:

```json
{
  "msg": "ok",
  "code": 200,
  "data": [
    {
      "code": "BK0901",
      "exchangeCode": "EM",
      "high": "0",
      "low": "0",
      "name": "3D摄像头",
      "open": "0",
      "preClose": "2002.92",
      "price": "2016.94"
    },
    {
      "code": "BK0603",
      "exchangeCode": "EM",
      "high": "0",
      "low": "0",
      "name": "页岩气",
      "open": "0",
      "preClose": "2560.61",
      "price": "2548.73"
    }
  ]
}
```

---

### <a id="api-35"></a>35. GET 板块列表

| 属性 | 值 |
|------|----|
| **路径** | `/api/sector/v1/sectorList` |
| **方法** | `GET` |
| **适用版本** | 按量计费、免费版、个人版、专业版、企业版 |

**请求参数**:

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| `token` | query | string | 否 | token,通过登录获取 |
| `countryCode` | query | string (CHN) | 是 | 国家/地区代码。（CHN：A股） |
| `exchangeCode` | query | string (EM) | 否 | 来源代码，默认EM。（EM：东方财富） |

**成功响应 (200)**:

| 字段名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `msg` | 字符串 | 是 | 响应消息 |
| `code` | 字符串 | 是 | 代码 |
| `data` | 数组 | 是 | 响应数据 |
| `data[].code` | 字符串 | 是 | 代码 |
| `data[].name` | 字符串 | 是 | 名称 |
| `data[].type` | 字符串 | 是 | 类型：（STOCK：股票，INDEX：指数，FUND：基金，FOREX：外汇，CRYPTO：加密货币，SECTOR：板块，BOND：债券，FUTURE：期货） |
| `data[].sectorType` | 字符串 | 是 | 板块类型。（INDUSTRY：行业板块，CONCEPT：概念板块，REGION：地域板块） |
| `data[].exchangeCode` | 字符串 | 是 | 来源代码。详见交易所清单接口。 |
| `data[].countryCode` | 字符串 | 是 | 国家/地区代码。详见国家/地区清单接口。 |

**响应示例**:

```json
{
  "msg": "ok",
  "code": 200,
  "data": [
    {
      "code": "BK1613",
      "name": "铝",
      "type": "SECTOR",
      "sectorType": "INDUSTRY",
      "exchangeCode": "EM",
      "countryCode": "CHN"
    },
    {
      "code": "BK1534",
      "name": "印刷",
      "type": "SECTOR",
      "sectorType": "INDUSTRY",
      "exchangeCode": "EM",
      "countryCode": "CHN"
    }
  ]
}
```

---

### <a id="api-36"></a>36. GET 板块排行

| 属性 | 值 |
|------|----|
| **路径** | `/api/sector/v1/sort` |
| **方法** | `GET` |
| **适用版本** | 按量计费、专业版、企业版 |

**请求参数**:

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| `token` | query | string | 否 | token,通过登录获取 |
| `countryCode` | query | string (CHN) | 否 | 国家/地区代码，和交易所，股票市场三选一。（CHN：中国大陆）） |
| `exchangeCode` | query | string (EM) | 否 | 来源代码，默认EM。（EM：东方财富） |
| `type` | query | string (all, industry, concept, region) | 否 | 类型。（all：所有，industry：行业，concept：概念，region：区域 |
| `sort` | query | string (price, change, changeRate, volume, amount, turnover, vr, sellVolume, buyVolume, netInflow, circulationValue, marketValue, circulationShares, totalShares, amplitude, open, high, low, preClose) | 否 | 排序方式。
（price：价格，change：涨跌额，changeRate：涨跌幅，volume：成交量，amount：成交额，
                turnover：换手率，vr：量比，sellVolume：内盘(主动卖出量)，buyVolume：外盘(主动买入量)，netInflow：净流入，circulationValue：流通市值，
                marketValue：总市值，circulationShares：流通股本，totalShares：总股本，amplitude：振幅，open：开盘价，high：最高价，low：最低价，preClose：昨收） |
| `order` | query | string (ASC, DESC) | 是 | 顺序：ASC 表升序，DESC 表降序（默认DESC） |
| `page` | query | string | 否 | 第几页，每页100行数据 |
| `format` | query | string (json, csv) | 否 | 格式,支持json格式和csv格式（默认json格式） |

**成功响应 (200)**:

| 字段名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `msg` | 字符串 | 是 | 响应消息 |
| `code` | 字符串 | 是 | 代码 |
| `data` | 对象 | 是 | 响应数据 |
| `data.pageNum` | 整数 | 是 |  |
| `data.pageTotal` | 整数 | 是 |  |
| `data.countTotal` | 整数 | 是 |  |
| `data.list` | 数组 | 是 |  |
| `data.list[].code` | 字符串 | 是 | 代码 |
| `data.list[].name` | 字符串 | 是 | 名称 |
| `data.list[].type` | 字符串 | 是 | 类型(STOCK：股票，INDEX：指数，FUND：基金，FOREX：外汇，CRYPTO：加密货币) |
| `data.list[].sectorType` | 字符串 | 是 | 板块类型（Industry：行业板块，Concept：概念板块，Region：地域板块）。 |
| `data.list[].exchangeCode` | 字符串 | 是 | 来源代码。详见交易所清单接口。 |
| `data.list[].countryCode` | 字符串 | 是 | 国家/地区代码。详见国家/地区清单接口。 |
| `data.list[].timestamp` | 整数 | 是 |  |
| `data.list[].localDate` | 字符串 | 是 | 时间 |
| `data.list[].price` | 实数 | 是 | 价格 |
| `data.list[].open` | 实数 | 是 | 开盘价 |
| `data.list[].high` | 实数 | 是 | 最高价 |
| `data.list[].low` | 实数 | 是 | 最低价 |
| `data.list[].preClose` | 实数 | 是 | 昨收 |
| `data.list[].volume` | 整数 | 是 | 成交量 |
| `data.list[].amount` | 实数 | 是 | 成交额 |
| `data.list[].change` | 实数 | 是 | 涨跌额 |
| `data.list[].changeRate` | 实数 | 是 | 涨跌幅 |
| `data.list[].mktCap` | 实数 | 是 | 总市值 |
| `data.list[].floatCap` | 实数 | 是 | 流通市值 |
| `data.list[].totShr` | 实数 | 是 | 总股本 |
| `data.list[].floatShr` | 实数 | 是 | 流通股本 |
| `data.list[].turnover` | 实数 | 是 | 换手率 |
| `data.list[].amplitude` | 实数 | 是 | 振幅 |
| `data.ordImbRatio` | 实数 | 是 | 委比 |
| `data.volRatio` | 实数 | 是 | 量比 |
| `data.activeSellVol` | 整数 | 是 | 内盘(主动卖出总量) |
| `data.activeBuyVol` | 整数 | 是 | 外盘(主动买入总量) |
| `data.netInflow` | 实数 | 是 | 净流入 |
| `data.riseCount` | 整数 | 是 | 上涨股票数量 |
| `data.fallCount` | 整数 | 是 | 下跌股票数量 |
| `data.flatCount` | 整数 | 是 | 持平股票数量 |
| `data.riseFirstStock` | 对象 | 是 | 涨幅最大的股票 |
| `data.fallFirstStock` | 对象 | 是 | 跌幅最大的股票 |

**响应示例**:

```json
{
  "msg": "ok",
  "code": 200,
  "data": {
    "pageNum": 1,
    "pageTotal": 10,
    "countTotal": 494,
    "list": [
      {
        "code": "BK1051",
        "name": "昨日连板_含一字",
        "type": "SECTOR",
        "sectorType": "CONCEPT",
        "exchangeCode": "EM",
        "countryCode": "CHN",
        "timestamp": 1782350199000,
        "localDate": "2026-06-25 09:16:39",
        "price": "24153.69",
        "open": "0",
        "high": "0",
        "low": "0",
        "preClose": "22736.59",
        "volume": "0",
        "amount": "0",
        "change": "1417.1",
        "changeRate": "6.2327",
        "mktCap": "183627835000",
        "floatCap": "141404300000",
        "totShr": "8288187648",
        "floatShr": "9780020480",
        "turnover": 0,
        "amplitude": 0
      },
      {
        "code": "BK1050",
        "name": "昨日涨停_含一字",
        "type": "SECTOR",
        "sectorType": "CONCEPT",
        "exchangeCode": "EM",
        "countryCode": "CHN",
        "timestamp": 1782350199000,
        "localDate": "2026-06-25 09:16:39",
        "price": "82284.24",
        "open": "0",
        "high": "0",
        "low": "0",
        "preClose": "77778.91",
        "volume": "0",
        "amount": "0",
        "change": "4505.33",
        "changeRate": "5.7925",
        "mktCap": "4122087344000",
        "floatCap": "3794494976000",
        "totShr": "101901385728",
        "floatShr": "110557704192",
        "turnover": 0,
        "amplitude": 0
      }
    ]
  }
}
```

---

### <a id="api-37"></a>37. GET 板块K线

| 属性 | 值 |
|------|----|
| **路径** | `/api/sector/v2/kline` |
| **方法** | `GET` |
| **适用版本** | 按量计费、免费版（不含分钟级数据）、个人版（不含分钟级数据）、专业版、企业版 |

**请求参数**:

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| `token` | query | string | 否 | token,通过登录获取 |
| `symbol` | query | string | 否 | 板块代码，A股可用cn开头，不加来源默认EM，也支持代码加来源后缀。 |
| `type` | query | string (day, day5, d1, w1, m1, y1) | 是 | k线类型， day：当日1分钟，day5：最近5个交易日1分钟，d1：日K，w1：周K，m1：月K，y1：年K。 |
| `beginDate` | query | string | 否 | 起始日期。格式“yyyy-mm-dd hh:mm:ss”。 |
| `endDate` | query | string | 否 | 结束日期。格式“yyyy-mm-dd hh:mm:ss”。 |
| `order` | query | string (ASC, DESC) | 否 | 顺序：ASC 表正序，DESC 表倒序（默认在不输入时间为倒序，只输入开始时间为正序，只输入结束时间为倒叙，输入开始时间和结束时间为倒序） |
| `limit` | query | string | 否 | 数量，默认：1000。（最大为2000） |
| `format` | query | string (json, csv) | 否 | 格式,支持json格式和csv格式（默认json格式） |

**成功响应 (200)**:

| 字段名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `msg` | 字符串 | 是 | 响应消息 |
| `code` | 字符串 | 是 | 代码 |
| `data` | 数组 | 是 | 响应数据 |
| `data[].date` | 字符串 | 是 | 更新时间 |
| `data[].close` | 字符串 | 是 | 收盘价 |
| `data[].open` | 字符串 | 是 | 开盘价格 |
| `data[].high` | 字符串 | 是 | 最高价 |
| `data[].low` | 字符串 | 是 | 最低价 |
| `data[].preClose` | 字符串 | 是 | 昨收 |
| `data[].volume` | 字符串 | 是 | 成交量 |
| `data[].amount` | 字符串 | 是 | 成交额 |
| `data[].time` | 整数 | 是 | 时间戳(毫秒) |

**响应示例**:

```json
{
  "msg": "ok",
  "code": 200,
  "data": [
    {
      "date": "2026-06-25",
      "close": "4194.26",
      "open": "0",
      "high": "0",
      "low": "0",
      "preClose": "4158.65",
      "volume": "0",
      "amount": "0"
    },
    {
      "date": "2026-06-24",
      "close": "4158.65",
      "open": "4173.63",
      "high": "4234.53",
      "low": "4139.53",
      "preClose": "4164.53",
      "volume": "10589750",
      "amount": "4674743990"
    }
  ]
}
```

---

### <a id="api-38"></a>38. GET 实时行情

| 属性 | 值 |
|------|----|
| **路径** | `/api/sector/v2/realtime` |
| **方法** | `GET` |
| **适用版本** | 按量计费、专业版、企业版 |

**请求参数**:

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| `token` | query | string | 否 | token,通过登录获取 |
| `symbol` | query | string | 是 | 板块代码，支持多个最多一次20个板块数据用英文逗号隔开，A股可用cn开头，不加来源默认EM，也支持代码加来源后缀。 |

**成功响应 (200)**:

| 字段名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `msg` | 字符串 | 是 | 响应消息 |
| `code` | 字符串 | 是 | 代码 |
| `data` | 数组 | 是 | 响应数据 |
| `data[].code` | 字符串 | 是 | 代码 |
| `data[].name` | 字符串 | 是 | 名称 |
| `data[].type` | 字符串 | 是 | 类型(STOCK：股票，INDEX：指数，FUND：基金，FOREX：外汇，CRYPTO：加密货币) |
| `data[].sectorType` | 字符串 | 是 | 板块类型（Industry：行业板块，Concept：概念板块，Region：地域板块）。 |
| `data[].exchangeCode` | 字符串 | 是 | 来源代码。详见交易所清单接口。 |
| `data[].countryCode` | 字符串 | 是 | 国家/地区代码。详见国家/地区清单接口。 |
| `data[].timestamp` | 整数 | 是 |  |
| `data[].localDate` | 字符串 | 是 | 时间 |
| `data[].price` | 实数 | 是 | 价格 |
| `data[].open` | 实数 | 是 | 开盘价 |
| `data[].high` | 实数 | 是 | 最高价 |
| `data[].low` | 实数 | 是 | 最低价 |
| `data[].preClose` | 实数 | 是 | 昨收 |
| `data[].volume` | 整数 | 是 | 成交量 |
| `data[].amount` | 实数 | 是 | 成交额 |
| `data[].change` | 实数 | 是 | 涨跌额 |
| `data[].changeRate` | 实数 | 是 | 涨跌幅 |
| `data[].mktCap` | 实数 | 是 | 总市值 |
| `data[].floatCap` | 实数 | 是 | 流通市值 |
| `data[].totShr` | 实数 | 是 | 总股本 |
| `data[].floatShr` | 实数 | 是 | 流通股本 |
| `data[].turnover` | 实数 | 是 | 换手率 |
| `data[].amplitude` | 实数 | 是 | 振幅 |
| `data[].ordImbRatio` | 实数 | 是 | 委比 |
| `data[].volRatio` | 实数 | 是 | 量比 |
| `data[].activeSellVol` | 整数 | 是 | 内盘(主动卖出总量) |
| `data[].activeBuyVol` | 整数 | 是 | 外盘(主动买入总量) |
| `data[].netInflow` | 实数 | 是 | 净流入 |
| `data[].riseCount` | 整数 | 是 | 上涨股票数量 |
| `data[].fallCount` | 整数 | 是 | 下跌股票数量 |
| `data[].flatCount` | 整数 | 是 | 持平股票数量 |
| `data[].riseFirstStock` | 对象 | 是 | 涨幅最大的股票 |
| `data[].fallFirstStock` | 对象 | 是 | 跌幅最大的股票 |

**响应示例**:

```json
{
  "msg": "ok",
  "code": 200,
  "data": [
    {
      "code": "BK0420",
      "name": "航空机场",
      "type": "SECTOR",
      "sectorType": "INDUSTRY",
      "exchangeCode": "EM",
      "countryCode": "CHN",
      "timestamp": 1782350202000,
      "localDate": "2026-06-25 09:16:42",
      "price": "4194.26",
      "open": "0",
      "high": "0",
      "low": "0",
      "preClose": "4158.65",
      "volume": "0",
      "amount": "0",
      "change": "35.61",
      "changeRate": "0.8563",
      "mktCap": "590370016000",
      "floatCap": "472163360000",
      "totShr": "106628063232",
      "floatShr": "128091820032",
      "turnover": 0,
      "amplitude": 0
    },
    {
      "code": "BK1090",
      "name": "机器人概念",
      "type": "SECTOR",
      "sectorType": "CONCEPT",
      "exchangeCode": "EM",
      "countryCode": "CHN",
      "timestamp": 1782350202000,
      "localDate": "2026-06-25 09:16:42",
      "price": "2165.98",
      "open": "0",
      "high": "0",
      "low": "0",
      "preClose": "2178.3",
      "volume": "0",
      "amount": "0",
      "change": "-12.32",
      "changeRate": "-0.5656",
      "mktCap": "15424518144000",
      "floatCap": "13324972800000",
      "totShr": "574502244352",
      "floatShr": "648094851072",
      "turnover": 0,
      "amplitude": 0
    }
  ]
}
```

---

### <a id="api-39"></a>39. GET 股票清单

| 属性 | 值 |
|------|----|
| **路径** | `/api/stock/v1/ahStockList` |
| **方法** | `GET` |
| **适用版本** | 按量计费、免费版、个人版、专业版、企业版 |

**请求参数**:

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| `token` | query | string | 否 | token,通过登录获取 |
| `format` | query | string (json, csv) | 否 | 格式,支持json格式和csv格式（默认json格式） |

**成功响应 (200)**:

| 字段名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `msg` | 字符串 | 是 | 响应消息 |
| `code` | 字符串 | 是 | 代码 |
| `data` | 数组 | 是 | 响应数据 |
| `data[].A` | 对象 | 是 |  |
| `data[].A.code` | 字符串 | 是 | 代码 |
| `data[].A.name` | 字符串 | 是 | 名称 |
| `data[].A.type` | 字符串 | 是 | 类型(STOCK：股票，INDEX：指数，FUND：基金，FOREX：外汇，CRYPTO：加密货币) |
| `data[].A.exchangeCode` | 字符串 | 是 | 交易所代码。详见交易所清单接口。 |
| `data[].A.countryCode` | 字符串 | 是 | 国家/地区代码。详见国家/地区清单接口。 |
| `data[].H` | 对象 | 是 |  |
| `data[].H.code` | 字符串 | 是 | 代码 |
| `data[].H.name` | 字符串 | 是 | 名称 |
| `data[].H.type` | 字符串 | 是 | 类型(STOCK：股票，INDEX：指数，FUND：基金，FOREX：外汇，CRYPTO：加密货币) |
| `data[].H.exchangeCode` | 字符串 | 是 | 交易所代码。详见交易所清单接口。 |
| `data[].H.countryCode` | 字符串 | 是 | 国家/地区代码。详见国家/地区清单接口。 |

**响应示例**:

```json
{
  "msg": "ok",
  "code": 200,
  "data": [
    {
      "A": {
        "code": "601319",
        "name": "中国人保",
        "type": "STOCK",
        "exchangeCode": "XSHG",
        "countryCode": "CHN"
      },
      "H": {
        "code": "01339",
        "name": "中国人民保险集团",
        "type": "STOCK",
        "exchangeCode": "XHKG",
        "countryCode": "HKG"
      }
    },
    {
      "A": {
        "code": "002714",
        "name": "牧原股份",
        "type": "STOCK",
        "exchangeCode": "XSHE",
        "countryCode": "CHN"
      },
      "H": {
        "code": "02714",
        "name": "牧原股份",
        "type": "STOCK",
        "exchangeCode": "XHKG",
        "countryCode": "HKG"
      }
    }
  ]
}
```

---

### <a id="api-40"></a>40. GET 资产负债表

| 属性 | 值 |
|------|----|
| **路径** | `/api/stock/v1/balanceSheet` |
| **方法** | `GET` |
| **适用版本** | 按量计费、免费版、个人版、专业版、企业版 |

**请求参数**:

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| `token` | query | string | 否 | token,通过登录获取 |
| `symbol` | query | string | 是 | 股票代码，上证用sh开头，深证用sz开头，北证用bj开头，港股用hk开头，美股用us开头。 |

**成功响应 (200)**:

| 字段名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `msg` | 字符串 | 是 | 响应消息 |
| `code` | 整数 | 是 | 响应状态码，200 表示成功 |
| `data` | 数组 | 是 | 响应数据 |
| `data[].reportDate` | 字符串 | 是 | 报告期 |
| `data[].announcementDate` | 字符串 | 是 | 公告日期 |
| `data[].disclosureDate` | 字符串 | 是 | 实际公示日期 |
| `data[].currency` | 字符串 | 是 | 币种 |
| `data[].fiscalYear` | 整数 | 是 | 财年 |
| `data[].fiscalPeriod` | 字符串 | 是 | 报告期类型(FY/Q1/H1等) |
| `data[].cashAndCashEquivalents` | 数字 | 是 | 现金及现金等价物 |
| `data[].cashAndShortTermInvestments` | 字符串 | 是 |  |
| `data[].accountsReceivable` | 数字 | 是 | 应收账款 |
| `data[].inventory` | 数字 | 是 | 存货 |
| `data[].prepaidExpenses` | 字符串 | 是 |  |
| `data[].otherCurrentAssets` | 字符串 | 是 |  |
| `data[].totalCurrentAssets` | 数字 | 是 | 流动资产合计 |
| `data[].propertyPlantAndEquipment` | 数字 | 是 | 固定资产 |
| `data[].intangibleAssets` | 数字 | 是 | 无形资产 |
| `data[].longTermInvestments` | 数字 | 是 | 长期股权投资 |
| `data[].deferredTaxAssets` | 数字 | 是 | 递延所得税资产 |
| `data[].otherNonCurrentAssets` | 字符串 | 是 |  |
| `data[].totalNonCurrentAssets` | 数字 | 是 | 非流动资产合计 |
| `data[].totalAssets` | 数字 | 是 | 资产总计 |
| `data[].accountsPayable` | 数字 | 是 | 应付账款 |
| `data[].currentPortionOfLongTermDebt` | 字符串 | 是 |  |
| `data[].deferredRevenue` | 字符串 | 是 |  |
| `data[].incomeTaxPayable` | 字符串 | 是 |  |
| `data[].otherCurrentLiabilities` | 字符串 | 是 |  |
| `data[].totalCurrentLiabilities` | 数字 | 是 | 流动负债合计 |
| `data[].deferredTaxLiabilities` | 字符串 | 是 |  |
| `data[].otherNonCurrentLiabilities` | 字符串 | 是 |  |
| `data[].totalNonCurrentLiabilities` | 数字 | 是 | 非流动负债合计 |
| `data[].totalLiabilities` | 数字 | 是 | 负债合计 |
| `data[].commonStock` | 数字 | 是 | 股本 |
| `data[].additionalPaidInCapital` | 数字 | 是 | 资本公积 |
| `data[].retainedEarnings` | 数字 | 是 | 未分配利润 |
| `data[].treasuryStock` | 数字 | 是 | 库存股 |
| `data[].accumulatedOtherComprehensiveIncome` | 字符串 | 是 |  |
| `data[].minorityInterest` | 数字 | 是 | 少数股东权益 |
| `data[].totalShareholdersEquity` | 数字 | 是 | 股东权益合计(不含少数股东) |
| `data[].totalEquity` | 数字 | 是 | 所有者权益总计(含少数股东) |
| `data[].totalLiabilitiesAndEquity` | 数字 | 是 | 负债与所有者权益总计 |
| `data[].sharesOutstanding` | 字符串 | 是 |  |
| `data[].shortTermInvestments` | 数字 | 是 | 短期投资/交易性金融资产 |
| `data[].goodwill` | 数字 | 是 | 商誉 |
| `data[].shortTermDebt` | 数字 | 是 | 短期借款 |
| `data[].longTermDebt` | 数字 | 是 | 长期借款 |

**响应示例**:

```json
{
  "msg": "ok",
  "code": 200,
  "data": [
    {
      "reportDate": "2026-03-31",
      "announcementDate": "2026-04-25",
      "disclosureDate": "2026-04-25",
      "currency": "CNY",
      "fiscalYear": 2026,
      "fiscalPeriod": "Q1",
      "cashAndCashEquivalents": "48786691397.55",
      "cashAndShortTermInvestments": "48786691397.55",
      "accountsReceivable": "32344588.37",
      "inventory": "60692316104.51",
      "prepaidExpenses": "28053418.89",
      "otherCurrentAssets": "192742681.88",
      "totalCurrentAssets": "271524528742.4",
      "propertyPlantAndEquipment": "22132684069.8",
      "intangibleAssets": "8611214393.29",
      "longTermInvestments": "3637268087.09",
      "deferredTaxAssets": "5687250277.39",
      "otherNonCurrentAssets": "144657424.59",
      "totalNonCurrentAssets": "48394316163.18",
      "totalAssets": "319918844905.58",
      "accountsPayable": "3671613767.68",
      "currentPortionOfLongTermDebt": "53309216",
      "deferredRevenue": "3027195224.08",
      "incomeTaxPayable": "7299360362.95",
      "otherCurrentLiabilities": "376773821.81",
      "totalCurrentLiabilities": "38455594988.88",
      "deferredTaxLiabilities": "79224591.6",
      "otherNonCurrentLiabilities": "248138889.41",
      "totalNonCurrentLiabilities": "327363481.01",
      "totalLiabilities": "38782958469.89",
      "commonStock": "1252270215",
      "additionalPaidInCapital": "1577095.18",
      "retainedEarnings": "219147661718.66",
      "treasuryStock": "1112188987.16",
      "accumulatedOtherComprehensiveIncome": "9299.65",
      "minorityInterest": "10241850759.42",
      "totalShareholdersEquity": "270894035676.27",
      "totalEquity": "281135886435.69",
      "totalLiabilitiesAndEquity": "319918844905.58",
      "sharesOutstanding": "1252270215"
    },
    {
      "reportDate": "2025-12-31",
      "announcementDate": "2026-04-17",
      "disclosureDate": "2026-04-17",
      "currency": "CNY",
      "fiscalYear": 2025,
      "fiscalPeriod": "FY",
      "cashAndCashEquivalents": "51690610946.5",
      "cashAndShortTermInvestments": "51690610946.5",
      "accountsReceivable": "2609048.49",
      "inventory": "61427421796.18",
      "prepaidExpenses": "6637314.31",
      "otherCurrentAssets": "51027010.56",
      "totalCurrentAssets": "252518662398.57",
      "propertyPlantAndEquipment": "22488122304.35",
      "intangibleAssets": "8685618688.56",
      "longTermInvestments": "4756753295.74",
      "deferredTaxAssets": "6602469151.22",
      "otherNonCurrentAssets": "175472981.42",
      "totalNonCurrentAssets": "51316181622.87",
      "totalAssets": "303834844021.44",
      "accountsPayable": "4007309049.87",
      "currentPortionOfLongTermDebt": "44206237.05",
      "accruedExpenses": "5298261266.22",
      "deferredRevenue": "8006739780.94",
      "incomeTaxPayable": "7697169830.69",
      "otherCurrentLiabilities": "994959710.24",
      "totalCurrentLiabilities": "49610476817.81",
      "deferredTaxLiabilities": "75608351.79",
      "otherNonCurrentLiabilities": "189504942.77",
      "totalNonCurrentLiabilities": "265113294.56",
      "totalLiabilities": "49875590112.37",
      "commonStock": "1252270215",
      "additionalPaidInCapital": "1577095.18",
      "retainedEarnings": "191905148832.21",
      "treasuryStock": "120112601.53",
      "accumulatedOtherComprehensiveIncome": "-5778843.62",
      "minorityInterest": "9321442876.89",
      "totalShareholdersEquity": "244637811032.18",
      "totalEquity": "253959253909.07",
      "totalLiabilitiesAndEquity": "303834844021.44",
      "sharesOutstanding": "1252270215"
    }
  ]
}
```

---

### <a id="api-41"></a>41. GET 企业现金流

| 属性 | 值 |
|------|----|
| **路径** | `/api/stock/v1/cashflow` |
| **方法** | `GET` |
| **适用版本** | 按量计费、免费版、个人版、专业版、企业版 |

**请求参数**:

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| `token` | query | string | 否 | token,通过登录获取 |
| `symbol` | query | string | 是 | 股票代码，上证用sh开头，深证用sz开头，北证用bj开头，港股用hk开头，美股用us开头。 |

**成功响应 (200)**:

| 字段名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `msg` | 字符串 | 是 | 响应消息 |
| `code` | 整数 | 是 | 响应状态码，200 表示成功 |
| `data` | 数组 | 是 | 响应数据 |
| `data[].reportDate` | 字符串 | 是 | 报告期 |
| `data[].announcementDate` | 字符串 | 是 | 公告日期 |
| `data[].disclosureDate` | 字符串 | 是 | 实际公示日期 |
| `data[].currency` | 字符串 | 是 | 币种 |
| `data[].fiscalYear` | 整数 | 是 | 财年 |
| `data[].fiscalPeriod` | 字符串 | 是 | 报告期类型 |
| `data[].industrySector` | 整数 | 是 | 行业类型(1工商业 2银行 3保险 4证券) |
| `data[].goodsSaleServicesRenderedCash` | 数字 | 是 | 销售商品、提供劳务收到的现金 |
| `data[].otherOperatingCashIn` | 数字 | 是 | 收到其他与经营活动有关的现金 |
| `data[].totalOperatingCashIn` | 数字 | 是 | 经营活动现金流入小计 |
| `data[].goodsPurchaseServicesPaidCash` | 数字 | 是 | 购买商品、接受劳务支付的现金 |
| `data[].employeeCashPaid` | 数字 | 是 | 支付给职工以及为职工支付的现金 |
| `data[].taxesPaid` | 数字 | 是 | 支付的各项税费 |
| `data[].otherOperatingCashOut` | 数字 | 是 | 支付其他与经营活动有关的现金 |
| `data[].totalOperatingCashOut` | 数字 | 是 | 经营活动现金流出小计 |
| `data[].netCashFromOperating` | 数字 | 是 | 经营活动产生的现金流量净额 |
| `data[].investmentRecoveryCash` | 数字 | 是 | 收回投资收到的现金 |
| `data[].investmentIncomeCash` | 数字 | 是 | 取得投资收益收到的现金 |
| `data[].fixedAssetDisposalCash` | 数字 | 是 | 处置固定资产、无形资产收回的现金 |
| `data[].totalInvestingCashIn` | 数字 | 是 | 投资活动现金流入小计 |
| `data[].fixedAssetPurchaseCash` | 数字 | 是 | 购建固定资产、无形资产支付的现金 |
| `data[].investmentPaymentCash` | 数字 | 是 | 投资支付的现金 |
| `data[].totalInvestingCashOut` | 数字 | 是 | 投资活动现金流出小计 |
| `data[].netCashFromInvesting` | 数字 | 是 | 投资活动产生的现金流量净额 |
| `data[].totalFinancingCashOut` | 数字 | 是 | 筹资活动现金流出小计 |
| `data[].netCashFromFinancing` | 数字 | 是 | 筹资活动产生的现金流量净额 |
| `data[].exchangeRateEffect` | 数字 | 是 | 汇率变动对现金的影响 |
| `data[].cashIncreaseAmount` | 数字 | 是 | 现金及现金等价物净增加额 |
| `data[].cashOpeningBalance` | 数字 | 是 | 期初现金及现金等价物余额 |
| `data[].cashClosingBalance` | 数字 | 是 | 期末现金及现金等价物余额 |
| `data[].refundOfTaxes` | 数字 | 是 | 收到的税费返还 |
| `data[].investmentReceivedCash` | 数字 | 是 | 吸收投资收到的现金 |
| `data[].borrowingReceivedCash` | 数字 | 是 | 取得借款收到的现金 |
| `data[].totalFinancingCashIn` | 数字 | 是 | 筹资活动现金流入小计 |
| `data[].debtRepaymentCash` | 数字 | 是 | 偿还债务支付的现金 |
| `data[].dividendProfitDistributionCash` | 数字 | 是 | 分配股利、利润或偿付利息支付的现金 |

**响应示例**:

```json
{
  "msg": "ok",
  "code": 200,
  "data": [
    {
      "reportDate": "2026-03-31",
      "announcementDate": "2026-04-25",
      "disclosureDate": "2026-04-25",
      "currency": "CNY",
      "fiscalYear": 2026,
      "fiscalPeriod": "Q1",
      "industrySector": 1,
      "goodsSaleServicesRenderedCash": "56392589148.92",
      "otherOperatingCashIn": "415433867.42",
      "totalOperatingCashIn": "56180964222.42",
      "goodsPurchaseServicesPaidCash": "3211261659.41",
      "employeeCashPaid": "7351815319.98",
      "taxesPaid": "24030967427.8",
      "otherOperatingCashOut": "1463836033.41",
      "totalOperatingCashOut": "29271072953.29",
      "netCashFromOperating": "26909891269.13",
      "investmentRecoveryCash": "39950000000",
      "investmentIncomeCash": "45339296.1",
      "fixedAssetDisposalCash": "11520",
      "totalInvestingCashIn": "39995651966.1",
      "fixedAssetPurchaseCash": "604791583.89",
      "investmentPaymentCash": "13750000000",
      "totalInvestingCashOut": "14356705468.75",
      "netCashFromInvesting": "25638946497.35",
      "totalFinancingCashOut": "1005514179.59",
      "netCashFromFinancing": "-1005514179.59",
      "exchangeRateEffect": "-705910.26",
      "cashIncreaseAmount": "51542617676.63",
      "cashOpeningBalance": "126425609447.72",
      "cashClosingBalance": "177968227124.35"
    },
    {
      "reportDate": "2026-03-31",
      "announcementDate": "2026-04-25",
      "disclosureDate": "2026-04-25",
      "currency": "CNY",
      "fiscalYear": 2026,
      "fiscalPeriod": "Q1",
      "industrySector": 1,
      "goodsSaleServicesRenderedCash": "56392589148.92",
      "otherOperatingCashIn": "415433867.42",
      "totalOperatingCashIn": "56180964222.42",
      "goodsPurchaseServicesPaidCash": "3211261659.41",
      "employeeCashPaid": "7351815319.98",
      "taxesPaid": "24030967427.8",
      "otherOperatingCashOut": "1463836033.41",
      "totalOperatingCashOut": "29271072953.29",
      "netCashFromOperating": "26909891269.13",
      "investmentRecoveryCash": "39950000000",
      "investmentIncomeCash": "45339296.1",
      "fixedAssetDisposalCash": "11520",
      "totalInvestingCashIn": "39995651966.1",
      "fixedAssetPurchaseCash": "604791583.89",
      "investmentPaymentCash": "13750000000",
      "totalInvestingCashOut": "14356705468.75",
      "netCashFromInvesting": "25638946497.35",
      "totalFinancingCashOut": "1005514179.59",
      "netCashFromFinancing": "-1005514179.59",
      "exchangeRateEffect": "-705910.26",
      "cashIncreaseAmount": "51542617676.63",
      "cashOpeningBalance": "126425609447.72",
      "cashClosingBalance": "177968227124.35"
    }
  ]
}
```

---

### <a id="api-42"></a>42. GET 企业现金流

| 属性 | 值 |
|------|----|
| **路径** | `/api/stock/v1/cashFlowStatement` |
| **方法** | `GET` |
| **适用版本** | 按量计费、免费版、个人版、专业版、企业版 |

**请求参数**:

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| `token` | query | string | 否 | token,通过登录获取 |
| `symbol` | query | string | 是 | 股票代码，上证用sh开头，深证用sz开头，北证用bj开头，港股用hk开头，美股用us开头。 |

**成功响应 (200)**:

| 字段名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `msg` | 字符串 | 是 | 响应消息 |
| `code` | 整数 | 是 | 响应状态码，200 表示成功 |
| `data` | 数组 | 是 | 响应数据 |
| `data[].reportDate` | 字符串 | 是 | 报告期 |
| `data[].announcementDate` | 字符串 | 是 | 公告日期 |
| `data[].disclosureDate` | 字符串 | 是 | 实际公示日期 |
| `data[].currency` | 字符串 | 是 | 币种 |
| `data[].fiscalYear` | 整数 | 是 | 财年 |
| `data[].fiscalPeriod` | 字符串 | 是 | 报告期类型 |
| `data[].industrySector` | 整数 | 是 | 行业类型(1工商业 2银行 3保险 4证券) |
| `data[].goodsSaleServicesRenderedCash` | 数字 | 是 | 销售商品、提供劳务收到的现金 |
| `data[].otherOperatingCashIn` | 数字 | 是 | 收到其他与经营活动有关的现金 |
| `data[].totalOperatingCashIn` | 数字 | 是 | 经营活动现金流入小计 |
| `data[].goodsPurchaseServicesPaidCash` | 数字 | 是 | 购买商品、接受劳务支付的现金 |
| `data[].employeeCashPaid` | 数字 | 是 | 支付给职工以及为职工支付的现金 |
| `data[].taxesPaid` | 数字 | 是 | 支付的各项税费 |
| `data[].otherOperatingCashOut` | 数字 | 是 | 支付其他与经营活动有关的现金 |
| `data[].totalOperatingCashOut` | 数字 | 是 | 经营活动现金流出小计 |
| `data[].netCashFromOperating` | 数字 | 是 | 经营活动产生的现金流量净额 |
| `data[].investmentRecoveryCash` | 数字 | 是 | 收回投资收到的现金 |
| `data[].investmentIncomeCash` | 数字 | 是 | 取得投资收益收到的现金 |
| `data[].fixedAssetDisposalCash` | 数字 | 是 | 处置固定资产、无形资产收回的现金 |
| `data[].totalInvestingCashIn` | 数字 | 是 | 投资活动现金流入小计 |
| `data[].fixedAssetPurchaseCash` | 数字 | 是 | 购建固定资产、无形资产支付的现金 |
| `data[].investmentPaymentCash` | 数字 | 是 | 投资支付的现金 |
| `data[].totalInvestingCashOut` | 数字 | 是 | 投资活动现金流出小计 |
| `data[].netCashFromInvesting` | 数字 | 是 | 投资活动产生的现金流量净额 |
| `data[].totalFinancingCashOut` | 数字 | 是 | 筹资活动现金流出小计 |
| `data[].netCashFromFinancing` | 数字 | 是 | 筹资活动产生的现金流量净额 |
| `data[].exchangeRateEffect` | 数字 | 是 | 汇率变动对现金的影响 |
| `data[].cashIncreaseAmount` | 数字 | 是 | 现金及现金等价物净增加额 |
| `data[].cashOpeningBalance` | 数字 | 是 | 期初现金及现金等价物余额 |
| `data[].cashClosingBalance` | 数字 | 是 | 期末现金及现金等价物余额 |
| `data[].refundOfTaxes` | 数字 | 是 | 收到的税费返还 |
| `data[].investmentReceivedCash` | 数字 | 是 | 吸收投资收到的现金 |
| `data[].borrowingReceivedCash` | 数字 | 是 | 取得借款收到的现金 |
| `data[].totalFinancingCashIn` | 数字 | 是 | 筹资活动现金流入小计 |
| `data[].debtRepaymentCash` | 数字 | 是 | 偿还债务支付的现金 |
| `data[].dividendProfitDistributionCash` | 数字 | 是 | 分配股利、利润或偿付利息支付的现金 |

**响应示例**:

```json
{
  "msg": "ok",
  "code": 200,
  "data": [
    {
      "reportDate": "2026-03-31",
      "announcementDate": "2026-04-25",
      "disclosureDate": "2026-04-25",
      "currency": "CNY",
      "fiscalYear": 2026,
      "fiscalPeriod": "Q1",
      "industrySector": 1,
      "goodsSaleServicesRenderedCash": "56392589148.92",
      "otherOperatingCashIn": "415433867.42",
      "totalOperatingCashIn": "56180964222.42",
      "goodsPurchaseServicesPaidCash": "3211261659.41",
      "employeeCashPaid": "7351815319.98",
      "taxesPaid": "24030967427.8",
      "otherOperatingCashOut": "1463836033.41",
      "totalOperatingCashOut": "29271072953.29",
      "netCashFromOperating": "26909891269.13",
      "investmentRecoveryCash": "39950000000",
      "investmentIncomeCash": "45339296.1",
      "fixedAssetDisposalCash": "11520",
      "totalInvestingCashIn": "39995651966.1",
      "fixedAssetPurchaseCash": "604791583.89",
      "investmentPaymentCash": "13750000000",
      "totalInvestingCashOut": "14356705468.75",
      "netCashFromInvesting": "25638946497.35",
      "totalFinancingCashOut": "1005514179.59",
      "netCashFromFinancing": "-1005514179.59",
      "exchangeRateEffect": "-705910.26",
      "cashIncreaseAmount": "51542617676.63",
      "cashOpeningBalance": "126425609447.72",
      "cashClosingBalance": "177968227124.35"
    },
    {
      "reportDate": "2026-03-31",
      "announcementDate": "2026-04-25",
      "disclosureDate": "2026-04-25",
      "currency": "CNY",
      "fiscalYear": 2026,
      "fiscalPeriod": "Q1",
      "industrySector": 1,
      "goodsSaleServicesRenderedCash": "56392589148.92",
      "otherOperatingCashIn": "415433867.42",
      "totalOperatingCashIn": "56180964222.42",
      "goodsPurchaseServicesPaidCash": "3211261659.41",
      "employeeCashPaid": "7351815319.98",
      "taxesPaid": "24030967427.8",
      "otherOperatingCashOut": "1463836033.41",
      "totalOperatingCashOut": "29271072953.29",
      "netCashFromOperating": "26909891269.13",
      "investmentRecoveryCash": "39950000000",
      "investmentIncomeCash": "45339296.1",
      "fixedAssetDisposalCash": "11520",
      "totalInvestingCashIn": "39995651966.1",
      "fixedAssetPurchaseCash": "604791583.89",
      "investmentPaymentCash": "13750000000",
      "totalInvestingCashOut": "14356705468.75",
      "netCashFromInvesting": "25638946497.35",
      "totalFinancingCashOut": "1005514179.59",
      "netCashFromFinancing": "-1005514179.59",
      "exchangeRateEffect": "-705910.26",
      "cashIncreaseAmount": "51542617676.63",
      "cashOpeningBalance": "126425609447.72",
      "cashClosingBalance": "177968227124.35"
    }
  ]
}
```

---

### <a id="api-43"></a>43. GET 企业信息

| 属性 | 值 |
|------|----|
| **路径** | `/api/stock/v1/companyInfo` |
| **方法** | `GET` |
| **适用版本** | 按量计费、免费版、个人版、专业版、企业版 |

**请求参数**:

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| `token` | query | string | 否 | token,通过登录获取 |
| `symbol` | query | string | 是 | 股票代码，上证用sh开头，深证用sz开头，北证用bj开头，港股用hk开头，美股用us开头。 |
| `format` | query | string (json, csv) | 否 | 格式,支持json格式和csv格式（默认json格式） |

**成功响应 (200)**:

| 字段名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `msg` | 字符串 | 是 | 响应消息 |
| `code` | 整数 | 是 | 响应状态码，200 表示成功 |
| `data` | 数组 | 是 | 响应数据 |
| `data[].code` | 字符串 | 是 |  |
| `data[].name` | 字符串 | 是 |  |
| `data[].type` | 字符串 | 是 |  |
| `data[].exchangeCode` | 字符串 | 是 |  |
| `data[].countryCode` | 字符串 | 是 |  |
| `data[].orgName` | 字符串 | 是 |  |
| `data[].secuCode` | 字符串 | 是 |  |
| `data[].securityCode` | 字符串 | 是 |  |
| `data[].securityNameAbbr` | 字符串 | 是 |  |
| `data[].securityTypeCode` | 字符串 | 是 |  |
| `data[].codeA` | 字符串 | 是 |  |
| `data[].nameA` | 字符串 | 是 |  |
| `data[].accountFirm` | 字符串 | 是 | 会计师事务所 |
| `data[].industry` | 字符串 | 是 | 行业 |
| `data[].address` | 字符串 | 是 | 公司地址 |
| `data[].chairman` | 字符串 | 是 | 委员长 |
| `data[].legalPerson` | 字符串 | 是 | 法人 |
| `data[].president` | 字符串 | 是 | 董事长 |
| `data[].regionBK` | 字符串 | 是 | 区域 |
| `data[].concepts` | 字符串 | 是 | 注册时间 |
| `data[].secretary` | 字符串 | 是 |  |
| `data[].foundDate` | 字符串 | 是 |  |
| `data[].regCapital` | 字符串 | 是 | 注册资本 |
| `data[].totalNum` | 字符串 | 是 | 员工数量 |
| `data[].orgTel` | 字符串 | 是 | 电话 |
| `data[].orgEmail` | 字符串 | 是 | 电子邮箱 |
| `data[].orgWeb` | 字符串 | 是 | 网址 |
| `data[].regAddress` | 字符串 | 是 | 注册地址 |
| `data[].orgProfile` | 字符串 | 是 | 公司简介 |
| `data[].profile` | 字符串 | 是 |  |
| `data[].mainBusiness` | 字符串 | 是 | 主营业务 |
| `data[].legalAdviser` | 字符串 | 是 | 法律顾问 |
| `data[].secretary"` | 字符串 | 是 | 董秘 |
| `data[].tatolNumber` | 字符串 | 是 | 高管数量 |

**响应示例**:

```json
{
  "msg": "ok",
  "code": 200,
  "data": [
    {
      "code": "600519",
      "name": "贵州茅台",
      "type": "STOCK",
      "exchangeCode": "XSHG",
      "countryCode": "CHN",
      "orgName": "贵州茅台酒股份有限公司",
      "secuCode": "600519.SH",
      "securityCode": "600519",
      "securityNameAbbr": "贵州茅台",
      "securityTypeCode": "058001001",
      "codeA": "600519.SH",
      "nameA": "贵州茅台",
      "accountFirm": "天健会计师事务所(特殊普通合伙)",
      "industry": "食品饮料-饮料-白酒",
      "address": "贵州省仁怀市茅台镇",
      "chairman": "陈华",
      "legalPerson": "陈华",
      "president": "王莉(代)",
      "regionBK": "贵州省",
      "concepts": "西部大开发,电商概念,央国企改革,超级品牌,白酒,酿酒概念,味蕾经济,HS300_,机构重仓,融资融券,央视50_,上证50_,上证180_,沪股通,证金持股,MSCI中国,富时罗素,标准普尔,茅指数,百元股,东方财富热股,行业龙头,权重股,大盘股,消费风格",
      "secretary": "余思明",
      "foundDate": "1999-11-20",
      "regCapital": 1250080000,
      "totalNum": 34992,
      "orgTel": "0851-22386002",
      "orgEmail": "mtdm@moutaichina.com",
      "orgWeb": "www.moutaichina.com",
      "regAddress": "贵州省仁怀市茅台镇",
      "orgProfile": "    贵州茅台酒股份有限公司(以下简称“公司”)成立于1999年11月20日,由中国贵州茅台酒厂(集团)有限责任公司(以下简称“茅台集团”)作为主发起人,联合另外七家单位共同发起设立,目前控股股东为茅台集团。公司总部位于贵州省北部风光旖旎的赤水河畔茅台镇,主营茅台酒及茅台酱香系列酒的生产与销售,主导产品贵州茅台酒是我国大曲酱香型白酒的鼻祖和典型代表,是有机食品和国家地理标志保护产品,是香飘世界的中国名片。2001年8月27日,公司股票在上海证券交易所上市交易。2025年,贵州茅台品牌价值达744.46亿美元,是“2025凯度BrandZ最具价值全球品牌100强”中全球最具价值的酒类品牌。",
      "profile": "高端白酒生产企业，世界三大蒸馏名酒之一，非物质文化遗产。",
      "mainBusiness": "茅台酒及系列酒的生产与销售",
      "legalAdviser": "北京市金杜律师事务所"
    }
  ]
}
```

---

### <a id="api-44"></a>44. GET 企业高管列表

| 属性 | 值 |
|------|----|
| **路径** | `/api/stock/v1/companyOfficer` |
| **方法** | `GET` |
| **适用版本** | 按量计费、免费版、个人版、专业版、企业版 |

**请求参数**:

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| `token` | query | string | 否 | token,通过登录获取 |
| `symbol` | query | string | 是 | 股票代码，上证用sh开头，深证用sz开头，北证用bj开头，港股用hk开头，美股用us开头。 |

**成功响应 (200)**:

| 字段名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `msg` | 字符串 | 是 | 响应消息 |
| `code` | 字符串 | 是 | 股票代码 |
| `data` | 数组 | 是 | 响应数据 |
| `data[].name` | 字符串 | 是 | 姓名 |
| `data[].title` | 字符串 | 是 | 官方头衔 |
| `data[].gender` | 字符串 | 是 | 性别(MALE/FEMALE/UNKNOWN) |
| `data[].age` | 整数 | 是 | 年龄 |
| `data[].birthYear` | 整数 | 是 | 出生年份 |
| `data[].education` | 字符串 | 是 | 学历 |
| `data[].nationality` | 字符串 | 是 | 国籍 |
| `data[].roleType` | 字符串 | 是 | 标准化角色类型(Chairman/CEO/CFO/Secretary/Director/Supervisor等) |
| `data[].appointmentDate` | 字符串 | 是 | 上任日期 |
| `data[].bio` | 字符串 | 是 | 个人简介 |
| `data[].nameCn` | 字符串 | 是 | 中文名 |
| `data[].isIndependent` | 布尔 | 是 | 是否独立董事 |
| `data[].isExecutive` | 布尔 | 是 | 是否执行董事 |
| `data[].isFounder` | 布尔 | 是 | 是否创始人 |
| `data[].resignationDate` | 字符串 | 是 | 离任日期 |
| `data[].compensation` | 数字 | 是 | 税前薪酬 |
| `data[].currency` | 字符串 | 是 | 薪酬币种 |
| `data[].sharesHeld` | 数字 | 是 | 持股数量 |
| `data[].optionsHeld` | 数字 | 是 | 持有期权数量 |

**响应示例**:

```json
{
  "msg": "ok",
  "code": 200,
  "data": [
    {
      "name": "陈华",
      "title": "董事长",
      "gender": "MALE",
      "age": 54,
      "birthYear": 1972,
      "education": "硕士",
      "nationality": "中国",
      "roleType": "Chairman",
      "appointmentDate": "2025-11-28",
      "bio": "男，彝族，1972年3月生，贵州盘州人，1994年7月参加工作，2001年6月加入中国共产党，大学学历、工程硕士、工商管理硕士，高级工程师，现任中国贵州茅台酒厂（集团）有限责任公司党委书记，贵州茅台酒股份有限公司党委书记。简历如下：1990.09--1994.07 焦作矿业学院采矿工程专业学习1994.07--1997.11 盘江矿务局土城矿采矿四区助理工程师1997.11--2004.02 先后任盘江煤电（集团）有限公司土城矿采矿二区技术主管，采矿三区助理工程师，采矿四区技术主管、副区长2004.02--2008.12 先后任贵州盘江煤电有限责任公司土城矿采矿三区区长、采矿四区副总工程师兼区长、驻土城矿安监处处长、土城矿副矿长（2007.12被评为高级工程师）2008.12--2009.09 贵州盘江马依煤业有限公司副总经理2009.09--2012.08 先后任盘江精煤股份有限公司土城矿副矿长、矿长2012.08--2013.04 盘江投资控股（集团）有限公司副总经理（2010.03--2012.12 中国矿业大学矿业工程领域工程硕士专业学习，获工程硕士学位）2013.04--2013.11 贵州林东矿业（集团）有限责任公司副董事长、总经理、党委副书记，林东煤业发展股份有限公司董事、总经理、党委委员（兼）2013.11--2014.01 贵州林东矿业（集团）有限责任公司副董事长、总经理、党委副书记，林东煤业发展股份有限公司董事、总经理、党委书记（兼）（2010.09--2013.12 中国矿业大学高级管理人员工商管理硕士专业学习，获工商管理硕士学位）2014.01--2014.03 贵州省安全生产监督管理局副局长、党组成员2014.03--2014.08 贵州省安全生产监督管理局副局长、党组成员，贵州煤矿安全监察局党组成员2014.08--2017.06 贵州省六盘水市副市长2017.06--2018.06 贵州盘江国有资本运营有限公司副董事长、总经理、党委副书记2018.06--2022.03 先后任贵州盘江煤电集团有限责任公司副董事长、总经理、党委副书记、党委书记、董事长2022.03--2025.10 贵州省能源局局长、党组书记2025.10-- 中国贵州茅台酒厂（集团）有限责任公司党委书记，贵州茅台酒股份有限公司党委书记。"
    },
    {
      "name": "陈华",
      "title": "董事",
      "gender": "MALE",
      "age": 54,
      "birthYear": 1972,
      "education": "硕士",
      "nationality": "中国",
      "roleType": "Director",
      "appointmentDate": "2025-11-28",
      "bio": "男，彝族，1972年3月生，贵州盘州人，1994年7月参加工作，2001年6月加入中国共产党，大学学历、工程硕士、工商管理硕士，高级工程师，现任中国贵州茅台酒厂（集团）有限责任公司党委书记，贵州茅台酒股份有限公司党委书记。简历如下：1990.09--1994.07 焦作矿业学院采矿工程专业学习1994.07--1997.11 盘江矿务局土城矿采矿四区助理工程师1997.11--2004.02 先后任盘江煤电（集团）有限公司土城矿采矿二区技术主管，采矿三区助理工程师，采矿四区技术主管、副区长2004.02--2008.12 先后任贵州盘江煤电有限责任公司土城矿采矿三区区长、采矿四区副总工程师兼区长、驻土城矿安监处处长、土城矿副矿长（2007.12被评为高级工程师）2008.12--2009.09 贵州盘江马依煤业有限公司副总经理2009.09--2012.08 先后任盘江精煤股份有限公司土城矿副矿长、矿长2012.08--2013.04 盘江投资控股（集团）有限公司副总经理（2010.03--2012.12 中国矿业大学矿业工程领域工程硕士专业学习，获工程硕士学位）2013.04--2013.11 贵州林东矿业（集团）有限责任公司副董事长、总经理、党委副书记，林东煤业发展股份有限公司董事、总经理、党委委员（兼）2013.11--2014.01 贵州林东矿业（集团）有限责任公司副董事长、总经理、党委副书记，林东煤业发展股份有限公司董事、总经理、党委书记（兼）（2010.09--2013.12 中国矿业大学高级管理人员工商管理硕士专业学习，获工商管理硕士学位）2014.01--2014.03 贵州省安全生产监督管理局副局长、党组成员2014.03--2014.08 贵州省安全生产监督管理局副局长、党组成员，贵州煤矿安全监察局党组成员2014.08--2017.06 贵州省六盘水市副市长2017.06--2018.06 贵州盘江国有资本运营有限公司副董事长、总经理、党委副书记2018.06--2022.03 先后任贵州盘江煤电集团有限责任公司副董事长、总经理、党委副书记、党委书记、董事长2022.03--2025.10 贵州省能源局局长、党组书记2025.10-- 中国贵州茅台酒厂（集团）有限责任公司党委书记，贵州茅台酒股份有限公司党委书记。"
    }
  ]
}
```

---

### <a id="api-45"></a>45. GET 企业高管列表

| 属性 | 值 |
|------|----|
| **路径** | `/api/stock/v1/companyOfficers` |
| **方法** | `GET` |
| **适用版本** | 按量计费、免费版、个人版、专业版、企业版 |

**请求参数**:

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| `token` | query | string | 否 | token,通过登录获取 |
| `symbol` | query | string | 是 | 股票代码，上证用sh开头，深证用sz开头，北证用bj开头，港股用hk开头，美股用us开头。 |

**成功响应 (200)**:

| 字段名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `msg` | 字符串 | 是 | 响应消息 |
| `code` | 字符串 | 是 | 股票代码 |
| `data` | 数组 | 是 | 响应数据 |
| `data[].name` | 字符串 | 是 | 姓名 |
| `data[].title` | 字符串 | 是 | 官方头衔 |
| `data[].gender` | 字符串 | 是 | 性别(MALE/FEMALE/UNKNOWN) |
| `data[].age` | 整数 | 是 | 年龄 |
| `data[].birthYear` | 整数 | 是 | 出生年份 |
| `data[].education` | 字符串 | 是 | 学历 |
| `data[].nationality` | 字符串 | 是 | 国籍 |
| `data[].roleType` | 字符串 | 是 | 标准化角色类型(Chairman/CEO/CFO/Secretary/Director/Supervisor等) |
| `data[].appointmentDate` | 字符串 | 是 | 上任日期 |
| `data[].bio` | 字符串 | 是 | 个人简介 |
| `data[].nameCn` | 字符串 | 是 | 中文名 |
| `data[].isIndependent` | 布尔 | 是 | 是否独立董事 |
| `data[].isExecutive` | 布尔 | 是 | 是否执行董事 |
| `data[].isFounder` | 布尔 | 是 | 是否创始人 |
| `data[].resignationDate` | 字符串 | 是 | 离任日期 |
| `data[].compensation` | 数字 | 是 | 税前薪酬 |
| `data[].currency` | 字符串 | 是 | 薪酬币种 |
| `data[].sharesHeld` | 数字 | 是 | 持股数量 |
| `data[].optionsHeld` | 数字 | 是 | 持有期权数量 |

**响应示例**:

```json
{
  "msg": "ok",
  "code": 200,
  "data": [
    {
      "name": "陈华",
      "title": "董事长",
      "gender": "MALE",
      "age": 54,
      "birthYear": 1972,
      "education": "硕士",
      "nationality": "中国",
      "roleType": "Chairman",
      "appointmentDate": "2025-11-28",
      "bio": "男，彝族，1972年3月生，贵州盘州人，1994年7月参加工作，2001年6月加入中国共产党，大学学历、工程硕士、工商管理硕士，高级工程师，现任中国贵州茅台酒厂（集团）有限责任公司党委书记，贵州茅台酒股份有限公司党委书记。简历如下：1990.09--1994.07 焦作矿业学院采矿工程专业学习1994.07--1997.11 盘江矿务局土城矿采矿四区助理工程师1997.11--2004.02 先后任盘江煤电（集团）有限公司土城矿采矿二区技术主管，采矿三区助理工程师，采矿四区技术主管、副区长2004.02--2008.12 先后任贵州盘江煤电有限责任公司土城矿采矿三区区长、采矿四区副总工程师兼区长、驻土城矿安监处处长、土城矿副矿长（2007.12被评为高级工程师）2008.12--2009.09 贵州盘江马依煤业有限公司副总经理2009.09--2012.08 先后任盘江精煤股份有限公司土城矿副矿长、矿长2012.08--2013.04 盘江投资控股（集团）有限公司副总经理（2010.03--2012.12 中国矿业大学矿业工程领域工程硕士专业学习，获工程硕士学位）2013.04--2013.11 贵州林东矿业（集团）有限责任公司副董事长、总经理、党委副书记，林东煤业发展股份有限公司董事、总经理、党委委员（兼）2013.11--2014.01 贵州林东矿业（集团）有限责任公司副董事长、总经理、党委副书记，林东煤业发展股份有限公司董事、总经理、党委书记（兼）（2010.09--2013.12 中国矿业大学高级管理人员工商管理硕士专业学习，获工商管理硕士学位）2014.01--2014.03 贵州省安全生产监督管理局副局长、党组成员2014.03--2014.08 贵州省安全生产监督管理局副局长、党组成员，贵州煤矿安全监察局党组成员2014.08--2017.06 贵州省六盘水市副市长2017.06--2018.06 贵州盘江国有资本运营有限公司副董事长、总经理、党委副书记2018.06--2022.03 先后任贵州盘江煤电集团有限责任公司副董事长、总经理、党委副书记、党委书记、董事长2022.03--2025.10 贵州省能源局局长、党组书记2025.10-- 中国贵州茅台酒厂（集团）有限责任公司党委书记，贵州茅台酒股份有限公司党委书记。"
    },
    {
      "name": "陈华",
      "title": "董事",
      "gender": "MALE",
      "age": 54,
      "birthYear": 1972,
      "education": "硕士",
      "nationality": "中国",
      "roleType": "Director",
      "appointmentDate": "2025-11-28",
      "bio": "男，彝族，1972年3月生，贵州盘州人，1994年7月参加工作，2001年6月加入中国共产党，大学学历、工程硕士、工商管理硕士，高级工程师，现任中国贵州茅台酒厂（集团）有限责任公司党委书记，贵州茅台酒股份有限公司党委书记。简历如下：1990.09--1994.07 焦作矿业学院采矿工程专业学习1994.07--1997.11 盘江矿务局土城矿采矿四区助理工程师1997.11--2004.02 先后任盘江煤电（集团）有限公司土城矿采矿二区技术主管，采矿三区助理工程师，采矿四区技术主管、副区长2004.02--2008.12 先后任贵州盘江煤电有限责任公司土城矿采矿三区区长、采矿四区副总工程师兼区长、驻土城矿安监处处长、土城矿副矿长（2007.12被评为高级工程师）2008.12--2009.09 贵州盘江马依煤业有限公司副总经理2009.09--2012.08 先后任盘江精煤股份有限公司土城矿副矿长、矿长2012.08--2013.04 盘江投资控股（集团）有限公司副总经理（2010.03--2012.12 中国矿业大学矿业工程领域工程硕士专业学习，获工程硕士学位）2013.04--2013.11 贵州林东矿业（集团）有限责任公司副董事长、总经理、党委副书记，林东煤业发展股份有限公司董事、总经理、党委委员（兼）2013.11--2014.01 贵州林东矿业（集团）有限责任公司副董事长、总经理、党委副书记，林东煤业发展股份有限公司董事、总经理、党委书记（兼）（2010.09--2013.12 中国矿业大学高级管理人员工商管理硕士专业学习，获工商管理硕士学位）2014.01--2014.03 贵州省安全生产监督管理局副局长、党组成员2014.03--2014.08 贵州省安全生产监督管理局副局长、党组成员，贵州煤矿安全监察局党组成员2014.08--2017.06 贵州省六盘水市副市长2017.06--2018.06 贵州盘江国有资本运营有限公司副董事长、总经理、党委副书记2018.06--2022.03 先后任贵州盘江煤电集团有限责任公司副董事长、总经理、党委副书记、党委书记、董事长2022.03--2025.10 贵州省能源局局长、党组书记2025.10-- 中国贵州茅台酒厂（集团）有限责任公司党委书记，贵州茅台酒股份有限公司党委书记。"
    }
  ]
}
```

---

### <a id="api-46"></a>46. GET 企业信息

| 属性 | 值 |
|------|----|
| **路径** | `/api/stock/v1/companyProfile` |
| **方法** | `GET` |
| **适用版本** | 按量计费、免费版、个人版、专业版、企业版 |

**请求参数**:

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| `token` | query | string | 否 | token,通过登录获取 |
| `symbol` | query | string | 是 | 股票代码，上证用sh开头，深证用sz开头，北证用bj开头，港股用hk开头，美股用us开头。 |
| `format` | query | string (json, csv) | 否 | 格式,支持json格式和csv格式（默认json格式） |

**成功响应 (200)**:

| 字段名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `msg` | 字符串 | 是 | 响应消息 |
| `code` | 整数 | 是 | 响应状态码，200 表示成功 |
| `data` | 数组 | 是 | 响应数据 |
| `data[].code` | 字符串 | 是 |  |
| `data[].name` | 字符串 | 是 |  |
| `data[].type` | 字符串 | 是 |  |
| `data[].exchangeCode` | 字符串 | 是 |  |
| `data[].countryCode` | 字符串 | 是 |  |
| `data[].orgName` | 字符串 | 是 | 机构名称 |
| `data[].secuCode` | 字符串 | 是 | 证券代码 |
| `data[].securityCode` | 字符串 | 是 | 证券代码 |
| `data[].securityNameAbbr` | 字符串 | 是 | 证券简称 |
| `data[].securityTypeCode` | 字符串 | 是 | 证券类别代码 |
| `data[].codeA` | 字符串 | 是 | A股代码 |
| `data[].nameA` | 字符串 | 是 | A股名称 |
| `data[].accountFirm` | 字符串 | 是 | 会计师事务所 |
| `data[].industry` | 字符串 | 是 | 所属行业 |
| `data[].address` | 字符串 | 是 | 办公地址 |
| `data[].chairman` | 字符串 | 是 | 董事长 |
| `data[].legalPerson` | 字符串 | 是 | 法定代表人 |
| `data[].president` | 字符串 | 是 | 总裁 |
| `data[].regionBK` | 字符串 | 是 | 所属地区 |
| `data[].concepts` | 字符串 | 是 | 所属概念 |
| `data[].secretary` | 字符串 | 是 | 董事会秘书 |
| `data[].foundDate` | 字符串 | 是 | 成立日期 |
| `data[].regCapital` | 整数 | 是 | 注册资本 |
| `data[].totalNum` | 整数 | 是 | 员工总数 |
| `data[].orgTel` | 字符串 | 是 | 联系电话 |
| `data[].orgEmail` | 字符串 | 是 | 联系邮箱 |
| `data[].orgWeb` | 字符串 | 是 | 公司网站 |
| `data[].regAddress` | 字符串 | 是 | 注册地址 |
| `data[].orgProfile` | 字符串 | 是 | 机构简介 |
| `data[].profile` | 字符串 | 是 | 公司简介 |
| `data[].mainBusiness` | 字符串 | 是 | 主营业务 |
| `data[].legalAdviser` | 字符串 | 是 | 法律顾问 |
| `data[].englishName` | 字符串 | 是 | 英文名称 |
| `data[].codeB` | 字符串 | 是 | B股代码 |
| `data[].codeH` | 字符串 | 是 | H股代码 |
| `data[].nameB` | 字符串 | 是 | B股名称 |
| `data[].nameH` | 字符串 | 是 | H股名称 |
| `data[].mainRelatedBank` | 字符串 | 是 | 主要往来银行 |

**响应示例**:

```json
{
  "msg": "ok",
  "code": 200,
  "data": [
    {
      "code": "600519",
      "name": "贵州茅台",
      "type": "STOCK",
      "exchangeCode": "XSHG",
      "countryCode": "CHN",
      "orgName": "贵州茅台酒股份有限公司",
      "secuCode": "600519.SH",
      "securityCode": "600519",
      "securityNameAbbr": "贵州茅台",
      "securityTypeCode": "058001001",
      "codeA": "600519.SH",
      "nameA": "贵州茅台",
      "accountFirm": "天健会计师事务所(特殊普通合伙)",
      "industry": "食品饮料-饮料-白酒",
      "address": "贵州省仁怀市茅台镇",
      "chairman": "陈华",
      "legalPerson": "陈华",
      "president": "王莉(代)",
      "regionBK": "贵州省",
      "concepts": "西部大开发,电商概念,央国企改革,超级品牌,白酒,酿酒概念,味蕾经济,HS300_,机构重仓,融资融券,央视50_,上证50_,上证180_,沪股通,证金持股,MSCI中国,富时罗素,标准普尔,茅指数,百元股,东方财富热股,行业龙头,权重股,大盘股,消费风格",
      "secretary": "余思明",
      "foundDate": "1999-11-20",
      "regCapital": 1250080000,
      "totalNum": 34992,
      "orgTel": "0851-22386002",
      "orgEmail": "mtdm@moutaichina.com",
      "orgWeb": "www.moutaichina.com",
      "regAddress": "贵州省仁怀市茅台镇",
      "orgProfile": "    贵州茅台酒股份有限公司(以下简称“公司”)成立于1999年11月20日,由中国贵州茅台酒厂(集团)有限责任公司(以下简称“茅台集团”)作为主发起人,联合另外七家单位共同发起设立,目前控股股东为茅台集团。公司总部位于贵州省北部风光旖旎的赤水河畔茅台镇,主营茅台酒及茅台酱香系列酒的生产与销售,主导产品贵州茅台酒是我国大曲酱香型白酒的鼻祖和典型代表,是有机食品和国家地理标志保护产品,是香飘世界的中国名片。2001年8月27日,公司股票在上海证券交易所上市交易。2025年,贵州茅台品牌价值达744.46亿美元,是“2025凯度BrandZ最具价值全球品牌100强”中全球最具价值的酒类品牌。",
      "profile": "高端白酒生产企业，世界三大蒸馏名酒之一，非物质文化遗产。",
      "mainBusiness": "茅台酒及系列酒的生产与销售",
      "legalAdviser": "北京市金杜律师事务所"
    }
  ]
}
```

---

### <a id="api-47"></a>47. GET 当日资金流向

| 属性 | 值 |
|------|----|
| **路径** | `/api/stock/v1/dailyMoneyflow` |
| **方法** | `GET` |
| **适用版本** | 按量计费、免费版、个人版、专业版、企业版 |

**请求参数**:

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| `token` | query | string | 否 | token,通过登录获取 |
| `symbol` | query | string | 是 | 股票代码，上证用sh开头，深证用sz开头，北证用bj开头 |

**成功响应 (200)**:

| 字段名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `msg` | 字符串 | 是 | 响应消息 |
| `code` | 整数 | 是 | 响应状态码，200 表示成功 |
| `data` | 对象 | 是 | 响应数据 |
| `data.mainInflow` | 实数 | 是 | 主力流入金额 |
| `data.mainOutflow` | 实数 | 是 | 主力流出金额 |
| `data.superLargeInflow` | 实数 | 是 | 特大单流入金额 |
| `data.superLargeOutflow` | 实数 | 是 | 特大单流出金额 |
| `data.largeInflow` | 实数 | 是 | 大单流入金额 |
| `data.largeOutflow` | 实数 | 是 | 大单流出金额 |
| `data.mediumInflow` | 实数 | 是 | 中单流入金额 |
| `data.mediumOutflow` | 实数 | 是 | 中单流出金额 |
| `data.smallInflow` | 实数 | 是 | 小单流入金额 |
| `data.smallOutflow` | 实数 | 是 | 小单流出金额 |

**响应示例**:

```json
{
  "msg": "ok",
  "code": 200,
  "data": {}
}
```

---

### <a id="api-48"></a>48. GET 交易快照

| 属性 | 值 |
|------|----|
| **路径** | `/api/stock/v1/detail` |
| **方法** | `GET` |
| **适用版本** | 按量计费、免费版、个人版、专业版、企业版 |

**请求参数**:

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| `token` | query | string | 否 | token,通过登录获取 |
| `symbol` | query | string | 是 | 股票代码，上证用sh开头，深证用sz开头，北证用bj开头 |
| `page` | query | string | 否 | 表示第几页，默认为空表示最末尾页。 |

**成功响应 (200)**:

| 字段名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `msg` | 字符串 | 是 | 响应消息 |
| `code` | 整数 | 是 | 响应状态码，200 表示成功 |
| `data` | 对象 | 是 | 响应数据 |
| `data.page` | 整数 | 是 | 当前是第几页 |
| `data.pageTotal` | 整数 | 是 | 总页数 |
| `data.index` | 整数 | 是 | 序号 |
| `data.date` | 字符串 | 是 | 成交时间 |
| `data.price` | 实数 | 是 | 成交价格 |
| `data.volume` | 实数 | 是 | 成交量 |
| `data.amount` | 实数 | 是 | 成交额 |
| `data.nature` | 'B' | 'S' | 'M' | 是 | B：买盘，S：卖盘，M：中性盘 |

**响应示例**:

```json
{
  "msg": "ok",
  "code": 200,
  "data": {}
}
```

---

### <a id="api-49"></a>49. GET 股票分红/送股/配股

| 属性 | 值 |
|------|----|
| **路径** | `/api/stock/v1/distribution` |
| **方法** | `GET` |
| **适用版本** | 按量计费、免费版、个人版、专业版、企业版 |

**请求参数**:

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| `token` | query | string | 否 | token,通过登录获取 |
| `symbol` | query | string | 是 | 股票代码，上证用sh开头，深证用sz开头，北证用bj开头，港股用hk开头，美股用us开头。 |
| `format` | query | string (json, csv) | 否 | 格式,支持json格式和csv格式（默认json格式） |

**成功响应 (200)**:

| 字段名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `msg` | 字符串 | 是 | 响应消息 |
| `code` | 整数 | 是 | 响应状态码，200 表示成功 |
| `data` | 数组 | 是 | 响应数据 |
| `data[].type` | 字符串 | 是 |  |
| `data[].fiscalYear` | 字符串 | 是 |  |
| `data[].announcementDate` | 字符串 | 是 | 公告日 |
| `data[].recordDate` | 字符串 | 是 | 股权登记日 |
| `data[].exDividendDate` | 字符串 | 是 |  |
| `data[].paymentDate` | 字符串 | 是 | 派发日 |
| `data[].progress` | 字符串 | 是 |  |
| `data[].currency` | 字符串 | 是 | 币种(CNY/USD/HKD) |
| `data[].cashPerShare` | 字符串 | 是 |  |
| `data[].isGrossAmount` | 布尔 | 是 |  |
| `data[].summary` | 字符串 | 是 |  |
| `data[].dividendType` | 字符串 | 是 | 分红类型(CASH:现金分红, STOCK_BONUS:送红股, CAPITAL_TRANSFER:转增股, SPLIT:拆股, RIGHTS_ISSUE:配股, SCRIP:代息股份) |
| `data[].cashAmount` | 数字 | 是 | 现金分红金额(每股税前) |
| `data[].stockRatio` | 数字 | 是 | 送股/转增比例 |
| `data[].rightsPrice` | 数字 | 是 | 配股价格 |
| `data[].exDate` | 字符串 | 是 | 除权除息日 |
| `data[].status` | 字符串 | 是 | 状态(PRE:预案, IMPLEMENTED:已实施) |
| `data[].description` | 字符串 | 是 | 原始描述 |

**响应示例**:

```json
{
  "msg": "ok",
  "code": 200,
  "data": [
    {
      "type": "ANNUAL",
      "fiscalYear": "2025年报",
      "announcementDate": "2026-06-22",
      "recordDate": "2026-06-25",
      "exDividendDate": "2026-06-26",
      "paymentDate": "2026-06-26",
      "progress": "CONFIRMED",
      "currency": "CNY",
      "cashPerShare": "28.02423",
      "isGrossAmount": true,
      "summary": "10派280.2423元"
    },
    {
      "type": "INTERIM",
      "fiscalYear": "2026半年报",
      "announcementDate": "2026-04-17",
      "progress": "PRE_ANNOUNCEMENT",
      "currency": "CNY",
      "summary": "分红金额上限不超过公司2026年上半年实现归属于上市公司股东的净利润"
    }
  ]
}
```

---

### <a id="api-50"></a>50. GET 股票交易所

| 属性 | 值 |
|------|----|
| **路径** | `/api/stock/v1/exchangeList` |
| **方法** | `GET` |
| **适用版本** | 按量计费、免费版、个人版、专业版、企业版 |

**请求参数**:

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| `token` | query | string | 否 | token,通过登录获取 |
| `format` | query | string (json, csv) | 否 | 格式,支持json格式和csv格式（默认json格式） |

**成功响应 (200)**:

| 字段名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `msg` | 字符串 | 是 | 响应消息 |
| `code` | 整数 | 是 | 响应状态码，200 表示成功 |
| `data` | 数组 | 是 | 响应数据 |
| `data[].type` | 字符串 | 是 | 类型(STOCK/INDEX/FUND等) |
| `data[].exchangeCode` | 字符串 | 是 | 交易所代码 |
| `data[].exchangeName` | 字符串 | 是 | 交易所名称 |
| `data[].exchangeNameShort` | 字符串 | 是 | 交易所简称 |
| `data[].countryCode` | 字符串 | 是 | 国家/地区代码。详见国家/地区清单接口。 |
| `data[].currencyCode` | 字符串 | 是 | 币种代码。详见币种清单接口。 |
| `data[].localOpen` | 时间 | 是 | 开盘时间（当地）。格式：hh:mm:ss。 |
| `data[].localClose` | 时间 | 是 | 收盘时间（当地）。格式：hh:mm:ss。 |
| `data[].beijingOpen` | 时间 | 是 | 开盘时间（北京）。格式：hh:mm:ss。 |
| `data[].beijingClose` | 时间 | 是 | 收盘时间（北京）。格式：hh:mm:ss。 |
| `data[].timezone` | 字符串 | 是 | 时区 |
| `data[].delay` | 字符串 | 是 | 延时 |
| `data[].notes` | 字符串 | 是 | 备注 |

**响应示例**:

```json
{
  "msg": "ok",
  "code": 200,
  "data": [
    {
      "type": "STOCK",
      "exchangeCode": "ASEX",
      "exchangeName": "雅典证券交易所",
      "exchangeNameShort": "雅典",
      "countryCode": "GRC",
      "currencyCode": "EUR",
      "localOpen": "10:30:00",
      "localClose": "17:00:00",
      "beijingOpen": "16:30:00",
      "beijingClose": "23:00:00",
      "timezone": "Europe/Athens",
      "delay": null,
      "notes": "冬令时"
    },
    {
      "type": "STOCK",
      "exchangeCode": "BJSE",
      "exchangeName": "北京证券交易所",
      "exchangeNameShort": "北交所",
      "countryCode": "CHN",
      "currencyCode": "CNY",
      "localOpen": "09:30:00",
      "localClose": "15:00:00",
      "beijingOpen": "09:00:00",
      "beijingClose": "15:00:00",
      "timezone": "Asia/Shanghai",
      "delay": "实时",
      "notes": null
    },
    {
      "type": "STOCK",
      "exchangeCode": "BVMF",
      "exchangeName": "巴西证券交易所",
      "exchangeNameShort": "巴西",
      "countryCode": "BRA",
      "currencyCode": "BRL",
      "localOpen": "10:00:00",
      "localClose": "17:15:00",
      "beijingOpen": "21:00:00",
      "beijingClose": "04:15:00",
      "timezone": "America/Paramaribo",
      "delay": "15分钟",
      "notes": "冬令时"
    },
    {
      "type": "STOCK",
      "exchangeCode": "MISX",
      "exchangeName": "莫斯科证券交易所",
      "exchangeNameShort": "莫斯科",
      "countryCode": "RUS",
      "currencyCode": "RUB",
      "localOpen": "10:00:00",
      "localClose": "18:50:00",
      "beijingOpen": "15:00:00",
      "beijingClose": "23:50:00",
      "timezone": "Europe/Moscow",
      "delay": null,
      "notes": null
    }
  ]
}
```

---

### <a id="api-51"></a>51. GET 财务信息

| 属性 | 值 |
|------|----|
| **路径** | `/api/stock/v1/financialInfo` |
| **方法** | `GET` |
| **适用版本** | 按量计费、免费版、个人版、专业版、企业版 |

**请求参数**:

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| `token` | query | string | 否 | token,通过登录获取 |
| `symbol` | query | string | 是 | 股票代码，上证用sh开头，深证用sz开头，北证用bj开头，港股用hk开头，美股用us开头。 |

**成功响应 (200)**:

| 字段名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `msg` | 字符串 | 是 | 响应消息 |
| `code` | 字符串 | 是 | 代码 |
| `data` | 对象 | 是 | 响应数据 |
| `data.page` | 整数 | 是 |  |
| `data.pageTotal` | 整数 | 是 |  |
| `data.countTotal` | 整数 | 是 |  |
| `data.list` | 数组 | 是 |  |
| `data.list[].ticker` | 对象 | 是 |  |
| `data.list[].ticker.code` | 字符串 | 是 | 代码 |
| `data.list[].ticker.name` | 字符串 | 是 | 名称 |
| `data.list[].ticker.exchangeCode` | 字符串 | 是 | 交易所代码。详见交易所清单接口。 |
| `data.list[].ticker.countryCode` | 字符串 | 是 | 国家/地区代码。详见国家/地区清单接口。 |
| `data.list[].ticker.type` | 字符串 | 是 | 类型(STOCK：股票，INDEX：指数，FUND：基金，FOREX：外汇，CRYPTO：加密货币) |
| `data.list[].data` | 对象 | 是 |  |
| `data.list[].data.date` | 字符串 | 是 |  |
| `data.list[].data.price` | 整数 | 是 |  |
| `data.list[].data.preClose` | 实数 | 是 |  |
| `data.list[].data.open` | 整数 | 是 |  |
| `data.list[].data.high` | 整数 | 是 |  |
| `data.list[].data.low` | 整数 | 是 |  |
| `data.list[].data.volume` | 整数 | 是 |  |
| `data.list[].data.amount` | 实数 | 是 |  |
| `data.list[].data.change` | 实数 | 是 |  |
| `data.list[].data.changeRate` | 实数 | 是 |  |
| `data.list[].data.sellVolume` | 整数 | 是 |  |
| `data.list[].data.buyVolume` | 整数 | 是 |  |
| `data.list[].data.circulationValue` | 实数 | 是 |  |
| `data.list[].data.marketValue` | 实数 | 是 |  |
| `data.list[].data.circulationShares` | 整数 | 是 |  |
| `data.list[].data.totalShares` | 整数 | 是 |  |
| `data.list[].data.committee` | 实数 | 是 |  |
| `data.list[].data.pb` | 实数 | 是 |  |
| `data.list[].data.turnover` | 实数 | 是 |  |
| `data.list[].data.pe_ttm` | 实数 | 是 |  |
| `data.list[].data.pe_dyn` | 实数 | 是 |  |
| `data.list[].data.pe_static` | 实数 | 是 |  |
| `data.list[].data.amplitude` | 实数 | 是 |  |
| `data.list[].data.highLimit` | 实数 | 是 |  |
| `data.list[].data.lowLimit` | 实数 | 是 |  |
| `data.list[].data.sells` | 数组 | 是 |  |
| `data.list[].data.buys` | 数组 | 是 |  |
| `data.chineseName` | 字符串 | 是 | 中文名称（美股）。 |

**响应示例**:

```json
{
  "msg": "ok",
  "code": 200,
  "data": {
    "page": 1,
    "pageTotal": 52,
    "countTotal": 5144,
    "list": [
      {
        "ticker": {
          "code": "600519",
          "name": "贵州茅台",
          "exchangeCode": "XSHG",
          "countryCode": "CHN",
          "type": "STOCK"
        },
        "data": {
          "date": "2025-05-15 06:04:06",
          "price": 1558,
          "preClose": 1551.99,
          "open": 1552,
          "high": 1565,
          "low": 1545,
          "volume": 21489,
          "amount": 333994.2729,
          "change": 6.00999999999999,
          "changeRate": 0.38724476317502,
          "sellVolume": 12211,
          "buyVolume": 9278,
          "circulationValue": 19571.56,
          "marketValue": 19571.56,
          "circulationShares": 1256197800,
          "totalShares": 1256197800,
          "committee": 9.09,
          "pb": 8.4,
          "turnover": 0.17,
          "pe_ttm": 22.7,
          "pe_dyn": 22.7,
          "pe_static": 22.7,
          "amplitude": 1.29,
          "highLimit": 1707.19,
          "lowLimit": 1396.79,
          "sells": [
            {
              "price": 1558,
              "volume": 27
            },
            {
              "price": 1557.57,
              "volume": 5
            },
            {
              "price": 1557.5,
              "volume": 1
            },
            {
              "price": 1557.21,
              "volume": 1
            },
            {
              "price": 1557.01,
              "volume": 2
            }
          ],
          "buys": [
            {
              "price": 1558.5,
              "volume": 1
            },
            {
              "price": 1558.68,
              "volume": 1
            },
            {
              "price": 1559.49,
              "volume": 1
            },
            {
              "price": 1560,
              "volume": 26
            },
            {
              "price": 1560.01,
              "volume": 1
            }
          ]
        }
      },
      {
        "ticker": {
          "code": "688256",
          "name": "寒武纪-U",
          "exchangeCode": "XSHG",
          "countryCode": "CHN",
          "type": "STOCK"
        },
        "data": {
          "date": "2025-05-15 06:04:04",
          "price": 619.88,
          "preClose": 637.7,
          "open": 630.5,
          "high": 634.84,
          "low": 614.5,
          "volume": 5295079,
          "amount": 330358.1375,
          "change": -17.8200000000001,
          "changeRate": -2.79441743766662,
          "sellVolume": 2395515,
          "buyVolume": 2899564,
          "circulationValue": 2587.73,
          "marketValue": 2587.73,
          "circulationShares": 417456753,
          "totalShares": 417456753,
          "committee": -15.83,
          "pb": 47.65,
          "turnover": 1.27,
          "pe_ttm": -583.88,
          "pe_dyn": -583.88,
          "pe_static": -583.88,
          "amplitude": 3.19,
          "highLimit": 765.24,
          "lowLimit": 510.16,
          "sells": [
            {
              "price": 619.87,
              "volume": 15
            },
            {
              "price": 619.85,
              "volume": 15
            },
            {
              "price": 619.83,
              "volume": 44
            },
            {
              "price": 619.82,
              "volume": 18
            },
            {
              "price": 619.81,
              "volume": 9
            }
          ],
          "buys": [
            {
              "price": 619.88,
              "volume": 105
            },
            {
              "price": 619.91,
              "volume": 2
            },
            {
              "price": 620,
              "volume": 12
            },
            {
              "price": 620.03,
              "volume": 5
            },
            {
              "price": 620.1,
              "volume": 15
            }
          ]
        }
      }
    ]
  }
}
```

---

### <a id="api-52"></a>52. GET 企业利润表

| 属性 | 值 |
|------|----|
| **路径** | `/api/stock/v1/incomeSheet` |
| **方法** | `GET` |
| **适用版本** | 按量计费、免费版、个人版、专业版、企业版 |

**请求参数**:

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| `token` | query | string | 否 | token,通过登录获取 |
| `symbol` | query | string | 是 | 股票代码，上证用sh开头，深证用sz开头，北证用bj开头，港股用hk开头，美股用us开头。 |

**成功响应 (200)**:

| 字段名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `msg` | 字符串 | 是 | 响应消息 |
| `code` | 整数 | 是 | 响应状态码，200 表示成功 |
| `data` | 数组 | 是 | 响应数据 |
| `data[].reportDate` | 字符串 | 是 | 报告期 |
| `data[].announcementDate` | 字符串 | 是 | 公告日期 |
| `data[].disclosureDate` | 字符串 | 是 | 实际公示日期 |
| `data[].currency` | 字符串 | 是 |  |
| `data[].fiscalYear` | 整数 | 是 |  |
| `data[].fiscalPeriod` | 字符串 | 是 |  |
| `data[].reportType` | 字符串 | 是 | 报告类型 |
| `data[].industrySector` | 字符串 | 是 | 公司类型 (1工商业 2银行 3保险 4证券) |
| `data[].periodType` | 字符串 | 是 | 报告期类型 |
| `data[].basicEps` | 字符串 | 是 | 基本每股收益 |
| `data[].dilutedEps` | 字符串 | 是 | 稀释每股收益 |
| `data[].totalRevenue` | 字符串 | 是 | 营业总收入 |
| `data[].operatingRevenue` | 字符串 | 是 | 营业收入 |
| `data[].interestIncome` | 字符串 | 是 | 利息收入 |
| `data[].fairValueChangeGain` | 字符串 | 是 | 公允价值变动收益 |
| `data[].investmentIncome` | 字符串 | 是 | 投资净收益 |
| `data[].assInvestIncome` | 字符串 | 是 | 对联营/合营企业投资收益 |
| `data[].otherIncome` | 字符串 | 是 | 其他收益 |
| `data[].assetDisposalIncome` | 字符串 | 是 | 资产处置收益 |
| `data[].totalOperatingCost` | 字符串 | 是 | 营业总成本 |
| `data[].costOfGoodsSold` | 字符串 | 是 | 营业成本 |
| `data[].taxesAndSurcharges` | 字符串 | 是 | 税金及附加 |
| `data[].sellingExpenses` | 字符串 | 是 | 销售费用 |
| `data[].administrativeExpenses` | 字符串 | 是 | 管理费用 |
| `data[].researchAndDevelopment` | 字符串 | 是 | 研发费用 |
| `data[].financialExpenses` | 字符串 | 是 | 财务费用 |
| `data[].interestExpense` | 字符串 | 是 | 其中：利息费用 |
| `data[].commissionExpense` | 字符串 | 是 | 手续费及佣金支出 |
| `data[].creditImpairmentLoss` | 字符串 | 是 | 信用减值损失 |
| `data[].operatingProfit` | 字符串 | 是 | 营业利润 |
| `data[].nonOperatingIncome` | 字符串 | 是 | 营业外收入 |
| `data[].nonOperatingExpense` | 字符串 | 是 | 营业外支出 |
| `data[].totalProfit` | 字符串 | 是 | 利润总额 |
| `data[].incomeTax` | 字符串 | 是 | 所得税费用 |
| `data[].netProfit` | 字符串 | 是 | 净利润（含少数股东损益） |
| `data[].netProfitToParent` | 字符串 | 是 | 净利润（归母/不含少数股东） |
| `data[].minorityInterest` | 字符串 | 是 | 少数股东损益 |
| `data[].otherComprehensiveIncome` | 字符串 | 是 | 其他综合收益 |
| `data[].totalComprehensiveIncome` | 字符串 | 是 | 综合收益总额 |
| `data[].compIncToParent` | 字符串 | 是 | 归属母公司综合收益 |
| `data[].compIncToMinority` | 字符串 | 是 | 归属少数股东综合收益 |
| `data[].ebit` | 字符串 | 是 | 息税前利润 |
| `data[].continuingProfit` | 字符串 | 是 | 持续经营净利润 |
| `data[].netCommissionIncome` | 字符串 | 是 | 手续费及佣金净收入 |
| `data[].exchangeGain` | 字符串 | 是 | 汇兑净收益 |
| `data[].netExposureHedging` | 字符串 | 是 | 净敞口套期收益 |
| `data[].earnedPremium` | 字符串 | 是 | 已赚保费 |
| `data[].premiumIncome` | 字符串 | 是 | 保险业务收入 |
| `data[].reinsuranceIncome` | 字符串 | 是 | 分保费收入 |
| `data[].netBrokerageIncome` | 字符串 | 是 | 代理买卖证券净收入 |
| `data[].netUnderwritingIncome` | 字符串 | 是 | 证券承销业务净收入 |
| `data[].netAssetMgmtIncome` | 字符串 | 是 | 受托资管业务净收入 |
| `data[].otherBusinessIncome` | 字符串 | 是 | 其他业务收入 |
| `data[].assetImpairmentLoss` | 字符串 | 是 | 资产减值损失 |
| `data[].otherAssetImpairment` | 字符串 | 是 | 其他资产减值损失 |
| `data[].refundOfPremium` | 字符串 | 是 | 退保金 |
| `data[].claimsPaid` | 字符串 | 是 | 赔付总支出 |
| `data[].insuranceLiabilityReserve` | 字符串 | 是 | 提取保险责任准备金 |
| `data[].policyholderDividends` | 字符串 | 是 | 保户红利支出 |
| `data[].reinsuranceExpense` | 字符串 | 是 | 分保费用 |
| `data[].recoveryOfClaims` | 字符串 | 是 | 摊回赔付支出 |
| `data[].recoveryOfReinsurance` | 字符串 | 是 | 摊回分保费用 |
| `data[].otherBusinessCost` | 字符串 | 是 | 其他业务成本 |
| `data[].nonCurrentAssetDisposalLoss` | 字符串 | 是 | 非流动资产处置净损失 |
| `data[].ebitda` | 字符串 | 是 | 息税折旧摊销前利润 |
| `data[].insuranceExpense` | 字符串 | 是 | 保险业务支出 |
| `data[].operatingExpense` | 字符串 | 是 | 营业支出 |
| `data[].discontinuedProfit` | 字符串 | 是 | 终止经营净利润 |
| `data[].netProfitCorrected` | 字符串 | 是 | 扣非后净利润（更正前） |
| `data[].undistributedProfit` | 字符串 | 是 | 年初未分配利润 |
| `data[].distributableProfit` | 字符串 | 是 | 可分配利润 |
| `data[].transferSurplusReserve` | 字符串 | 是 | 盈余公积转入 |
| `data[].transferHousingFund` | 字符串 | 是 | 住房周转金转入 |
| `data[].transferOther` | 字符串 | 是 | 其他转入 |
| `data[].adjustmentLossGain` | 字符串 | 是 | 调整以前年度损益 |
| `data[].withdrawLegalSurplus` | 字符串 | 是 | 提取法定盈余公积 |
| `data[].withdrawLegalPubFund` | 字符串 | 是 | 提取法定公益金 |
| `data[].withdrawBizDevFund` | 字符串 | 是 | 提取企业发展基金 |
| `data[].withdrawReserveFund` | 字符串 | 是 | 提取储备基金 |
| `data[].withdrawDiscretionary` | 字符串 | 是 | 提取任意盈余公积 |
| `data[].staffWelfare` | 字符串 | 是 | 职工奖金福利 |
| `data[].profitToShareholders` | 字符串 | 是 | 可供股东分配利润 |
| `data[].dividendPreferred` | 字符串 | 是 | 应付优先股股利 |
| `data[].dividendCommon` | 字符串 | 是 | 应付普通股股利 |
| `data[].stockDividend` | 字符串 | 是 | 转作股本的普通股股利 |

**响应示例**:

```json
{
  "msg": "ok",
  "code": 200,
  "data": [
    {
      "reportDate": "2026-03-31",
      "announcementDate": "2026-04-25",
      "disclosureDate": "2026-04-25",
      "currency": "CNY",
      "fiscalYear": 2026,
      "fiscalPeriod": "Q1",
      "reportType": "1",
      "industrySector": 1,
      "periodType": "1",
      "basicEps": "21.76",
      "dilutedEps": "21.76",
      "totalRevenue": "54702912385.23",
      "operatingRevenue": "53909252220.51",
      "interestIncome": "793660164.72",
      "fairValueChangeGain": "-3077007.2",
      "investmentIncome": "434629.49",
      "assInvestIncome": "87268.16",
      "otherIncome": "2970996.16",
      "assetDisposalIncome": "130409.49",
      "totalOperatingCost": "17192223524.71",
      "costOfGoodsSold": "5520729200.32",
      "taxesAndSurcharges": "8227407160.96",
      "sellingExpenses": "1605764764.88",
      "administrativeExpenses": "1853763865.81",
      "researchAndDevelopment": "59310724.46",
      "financialExpenses": "-115803334.98",
      "interestExpense": "15366726.62",
      "commissionExpense": "118272.18",
      "creditImpairmentLoss": "25860797.96",
      "operatingProfit": "37537008686.42",
      "nonOperatingIncome": "6759734.6",
      "nonOperatingExpense": "518777",
      "totalProfit": "37543249644.02",
      "incomeTax": "9389418154.13",
      "netProfit": "28153831489.89",
      "netProfitToParent": "27242512886.45",
      "minorityInterest": "911318603.44",
      "otherComprehensiveIncome": "14877422.36",
      "totalComprehensiveIncome": "28168708912.25",
      "compIncToParent": "27248301029.72",
      "compIncToMinority": "920407882.53",
      "ebit": "37423717319.66",
      "continuingProfit": "28153831489.89"
    },
    {
      "reportDate": "2026-03-31",
      "announcementDate": "2026-04-25",
      "disclosureDate": "2026-04-25",
      "currency": "CNY",
      "fiscalYear": 2026,
      "fiscalPeriod": "Q1",
      "reportType": "1",
      "industrySector": 1,
      "periodType": "1",
      "basicEps": "21.76",
      "dilutedEps": "21.76",
      "totalRevenue": "54702912385.23",
      "operatingRevenue": "53909252220.51",
      "interestIncome": "793660164.72",
      "fairValueChangeGain": "-3077007.2",
      "investmentIncome": "434629.49",
      "assInvestIncome": "87268.16",
      "otherIncome": "2970996.16",
      "assetDisposalIncome": "130409.49",
      "totalOperatingCost": "17192223524.71",
      "costOfGoodsSold": "5520729200.32",
      "taxesAndSurcharges": "8227407160.96",
      "sellingExpenses": "1605764764.88",
      "administrativeExpenses": "1853763865.81",
      "researchAndDevelopment": "59310724.46",
      "financialExpenses": "-115803334.98",
      "interestExpense": "15366726.62",
      "commissionExpense": "118272.18",
      "creditImpairmentLoss": "25860797.96",
      "operatingProfit": "37537008686.42",
      "nonOperatingIncome": "6759734.6",
      "nonOperatingExpense": "518777",
      "totalProfit": "37543249644.02",
      "incomeTax": "9389418154.13",
      "netProfit": "28153831489.89",
      "netProfitToParent": "27242512886.45",
      "minorityInterest": "911318603.44",
      "otherComprehensiveIncome": "14877422.36",
      "totalComprehensiveIncome": "28168708912.25",
      "compIncToParent": "27248301029.72",
      "compIncToMinority": "920407882.53",
      "continuingProfit": "28153831489.89"
    }
  ]
}
```

---

### <a id="api-53"></a>53. GET 企业利润表

| 属性 | 值 |
|------|----|
| **路径** | `/api/stock/v1/incomeStatement` |
| **方法** | `GET` |
| **适用版本** | 按量计费、免费版、个人版、专业版、企业版 |

**请求参数**:

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| `token` | query | string | 否 | token,通过登录获取 |
| `symbol` | query | string | 是 | 股票代码，上证用sh开头，深证用sz开头，北证用bj开头，港股用hk开头，美股用us开头。 |

**成功响应 (200)**:

| 字段名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `msg` | 字符串 | 是 | 响应消息 |
| `code` | 整数 | 是 | 响应状态码，200 表示成功 |
| `data` | 数组 | 是 | 响应数据 |
| `data[].reportDate` | 字符串 | 是 | 报告期 |
| `data[].announcementDate` | 字符串 | 是 | 公告日期 |
| `data[].disclosureDate` | 字符串 | 是 | 实际公示日期 |
| `data[].currency` | 字符串 | 是 |  |
| `data[].fiscalYear` | 整数 | 是 |  |
| `data[].fiscalPeriod` | 字符串 | 是 |  |
| `data[].reportType` | 字符串 | 是 | 报告类型 |
| `data[].industrySector` | 字符串 | 是 | 公司类型 (1工商业 2银行 3保险 4证券) |
| `data[].periodType` | 字符串 | 是 | 报告期类型 |
| `data[].basicEps` | 字符串 | 是 | 基本每股收益 |
| `data[].dilutedEps` | 字符串 | 是 | 稀释每股收益 |
| `data[].totalRevenue` | 字符串 | 是 | 营业总收入 |
| `data[].operatingRevenue` | 字符串 | 是 | 营业收入 |
| `data[].interestIncome` | 字符串 | 是 | 利息收入 |
| `data[].fairValueChangeGain` | 字符串 | 是 | 公允价值变动收益 |
| `data[].investmentIncome` | 字符串 | 是 | 投资净收益 |
| `data[].assInvestIncome` | 字符串 | 是 | 对联营/合营企业投资收益 |
| `data[].otherIncome` | 字符串 | 是 | 其他收益 |
| `data[].assetDisposalIncome` | 字符串 | 是 | 资产处置收益 |
| `data[].totalOperatingCost` | 字符串 | 是 | 营业总成本 |
| `data[].costOfGoodsSold` | 字符串 | 是 | 营业成本 |
| `data[].taxesAndSurcharges` | 字符串 | 是 | 税金及附加 |
| `data[].sellingExpenses` | 字符串 | 是 | 销售费用 |
| `data[].administrativeExpenses` | 字符串 | 是 | 管理费用 |
| `data[].researchAndDevelopment` | 字符串 | 是 | 研发费用 |
| `data[].financialExpenses` | 字符串 | 是 | 财务费用 |
| `data[].interestExpense` | 字符串 | 是 | 其中：利息费用 |
| `data[].commissionExpense` | 字符串 | 是 | 手续费及佣金支出 |
| `data[].creditImpairmentLoss` | 字符串 | 是 | 信用减值损失 |
| `data[].operatingProfit` | 字符串 | 是 | 营业利润 |
| `data[].nonOperatingIncome` | 字符串 | 是 | 营业外收入 |
| `data[].nonOperatingExpense` | 字符串 | 是 | 营业外支出 |
| `data[].totalProfit` | 字符串 | 是 | 利润总额 |
| `data[].incomeTax` | 字符串 | 是 | 所得税费用 |
| `data[].netProfit` | 字符串 | 是 | 净利润（含少数股东损益） |
| `data[].netProfitToParent` | 字符串 | 是 | 净利润（归母/不含少数股东） |
| `data[].minorityInterest` | 字符串 | 是 | 少数股东损益 |
| `data[].otherComprehensiveIncome` | 字符串 | 是 | 其他综合收益 |
| `data[].totalComprehensiveIncome` | 字符串 | 是 | 综合收益总额 |
| `data[].compIncToParent` | 字符串 | 是 | 归属母公司综合收益 |
| `data[].compIncToMinority` | 字符串 | 是 | 归属少数股东综合收益 |
| `data[].ebit` | 字符串 | 是 | 息税前利润 |
| `data[].continuingProfit` | 字符串 | 是 | 持续经营净利润 |
| `data[].netCommissionIncome` | 字符串 | 是 | 手续费及佣金净收入 |
| `data[].exchangeGain` | 字符串 | 是 | 汇兑净收益 |
| `data[].netExposureHedging` | 字符串 | 是 | 净敞口套期收益 |
| `data[].earnedPremium` | 字符串 | 是 | 已赚保费 |
| `data[].premiumIncome` | 字符串 | 是 | 保险业务收入 |
| `data[].reinsuranceIncome` | 字符串 | 是 | 分保费收入 |
| `data[].netBrokerageIncome` | 字符串 | 是 | 代理买卖证券净收入 |
| `data[].netUnderwritingIncome` | 字符串 | 是 | 证券承销业务净收入 |
| `data[].netAssetMgmtIncome` | 字符串 | 是 | 受托资管业务净收入 |
| `data[].otherBusinessIncome` | 字符串 | 是 | 其他业务收入 |
| `data[].assetImpairmentLoss` | 字符串 | 是 | 资产减值损失 |
| `data[].otherAssetImpairment` | 字符串 | 是 | 其他资产减值损失 |
| `data[].refundOfPremium` | 字符串 | 是 | 退保金 |
| `data[].claimsPaid` | 字符串 | 是 | 赔付总支出 |
| `data[].insuranceLiabilityReserve` | 字符串 | 是 | 提取保险责任准备金 |
| `data[].policyholderDividends` | 字符串 | 是 | 保户红利支出 |
| `data[].reinsuranceExpense` | 字符串 | 是 | 分保费用 |
| `data[].recoveryOfClaims` | 字符串 | 是 | 摊回赔付支出 |
| `data[].recoveryOfReinsurance` | 字符串 | 是 | 摊回分保费用 |
| `data[].otherBusinessCost` | 字符串 | 是 | 其他业务成本 |
| `data[].nonCurrentAssetDisposalLoss` | 字符串 | 是 | 非流动资产处置净损失 |
| `data[].ebitda` | 字符串 | 是 | 息税折旧摊销前利润 |
| `data[].insuranceExpense` | 字符串 | 是 | 保险业务支出 |
| `data[].operatingExpense` | 字符串 | 是 | 营业支出 |
| `data[].discontinuedProfit` | 字符串 | 是 | 终止经营净利润 |
| `data[].netProfitCorrected` | 字符串 | 是 | 扣非后净利润（更正前） |
| `data[].undistributedProfit` | 字符串 | 是 | 年初未分配利润 |
| `data[].distributableProfit` | 字符串 | 是 | 可分配利润 |
| `data[].transferSurplusReserve` | 字符串 | 是 | 盈余公积转入 |
| `data[].transferHousingFund` | 字符串 | 是 | 住房周转金转入 |
| `data[].transferOther` | 字符串 | 是 | 其他转入 |
| `data[].adjustmentLossGain` | 字符串 | 是 | 调整以前年度损益 |
| `data[].withdrawLegalSurplus` | 字符串 | 是 | 提取法定盈余公积 |
| `data[].withdrawLegalPubFund` | 字符串 | 是 | 提取法定公益金 |
| `data[].withdrawBizDevFund` | 字符串 | 是 | 提取企业发展基金 |
| `data[].withdrawReserveFund` | 字符串 | 是 | 提取储备基金 |
| `data[].withdrawDiscretionary` | 字符串 | 是 | 提取任意盈余公积 |
| `data[].staffWelfare` | 字符串 | 是 | 职工奖金福利 |
| `data[].profitToShareholders` | 字符串 | 是 | 可供股东分配利润 |
| `data[].dividendPreferred` | 字符串 | 是 | 应付优先股股利 |
| `data[].dividendCommon` | 字符串 | 是 | 应付普通股股利 |
| `data[].stockDividend` | 字符串 | 是 | 转作股本的普通股股利 |

**响应示例**:

```json
{
  "msg": "ok",
  "code": 200,
  "data": [
    {
      "reportDate": "2026-03-31",
      "announcementDate": "2026-04-25",
      "disclosureDate": "2026-04-25",
      "currency": "CNY",
      "fiscalYear": 2026,
      "fiscalPeriod": "Q1",
      "reportType": "1",
      "industrySector": 1,
      "periodType": "1",
      "basicEps": "21.76",
      "dilutedEps": "21.76",
      "totalRevenue": "54702912385.23",
      "operatingRevenue": "53909252220.51",
      "interestIncome": "793660164.72",
      "fairValueChangeGain": "-3077007.2",
      "investmentIncome": "434629.49",
      "assInvestIncome": "87268.16",
      "otherIncome": "2970996.16",
      "assetDisposalIncome": "130409.49",
      "totalOperatingCost": "17192223524.71",
      "costOfGoodsSold": "5520729200.32",
      "taxesAndSurcharges": "8227407160.96",
      "sellingExpenses": "1605764764.88",
      "administrativeExpenses": "1853763865.81",
      "researchAndDevelopment": "59310724.46",
      "financialExpenses": "-115803334.98",
      "interestExpense": "15366726.62",
      "commissionExpense": "118272.18",
      "creditImpairmentLoss": "25860797.96",
      "operatingProfit": "37537008686.42",
      "nonOperatingIncome": "6759734.6",
      "nonOperatingExpense": "518777",
      "totalProfit": "37543249644.02",
      "incomeTax": "9389418154.13",
      "netProfit": "28153831489.89",
      "netProfitToParent": "27242512886.45",
      "minorityInterest": "911318603.44",
      "otherComprehensiveIncome": "14877422.36",
      "totalComprehensiveIncome": "28168708912.25",
      "compIncToParent": "27248301029.72",
      "compIncToMinority": "920407882.53",
      "ebit": "37423717319.66",
      "continuingProfit": "28153831489.89"
    },
    {
      "reportDate": "2026-03-31",
      "announcementDate": "2026-04-25",
      "disclosureDate": "2026-04-25",
      "currency": "CNY",
      "fiscalYear": 2026,
      "fiscalPeriod": "Q1",
      "reportType": "1",
      "industrySector": 1,
      "periodType": "1",
      "basicEps": "21.76",
      "dilutedEps": "21.76",
      "totalRevenue": "54702912385.23",
      "operatingRevenue": "53909252220.51",
      "interestIncome": "793660164.72",
      "fairValueChangeGain": "-3077007.2",
      "investmentIncome": "434629.49",
      "assInvestIncome": "87268.16",
      "otherIncome": "2970996.16",
      "assetDisposalIncome": "130409.49",
      "totalOperatingCost": "17192223524.71",
      "costOfGoodsSold": "5520729200.32",
      "taxesAndSurcharges": "8227407160.96",
      "sellingExpenses": "1605764764.88",
      "administrativeExpenses": "1853763865.81",
      "researchAndDevelopment": "59310724.46",
      "financialExpenses": "-115803334.98",
      "interestExpense": "15366726.62",
      "commissionExpense": "118272.18",
      "creditImpairmentLoss": "25860797.96",
      "operatingProfit": "37537008686.42",
      "nonOperatingIncome": "6759734.6",
      "nonOperatingExpense": "518777",
      "totalProfit": "37543249644.02",
      "incomeTax": "9389418154.13",
      "netProfit": "28153831489.89",
      "netProfitToParent": "27242512886.45",
      "minorityInterest": "911318603.44",
      "otherComprehensiveIncome": "14877422.36",
      "totalComprehensiveIncome": "28168708912.25",
      "compIncToParent": "27248301029.72",
      "compIncToMinority": "920407882.53",
      "continuingProfit": "28153831489.89"
    }
  ]
}
```

---

### <a id="api-54"></a>54. GET 资金流向

| 属性 | 值 |
|------|----|
| **路径** | `/api/stock/v1/moneyflow` |
| **方法** | `GET` |
| **适用版本** | 按量计费、免费版、个人版、专业版、企业版 |

**请求参数**:

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| `token` | query | string | 否 | token,通过登录获取 |
| `symbol` | query | string | 是 | 股票代码，上证用sh开头，深证用sz开头，北证用bj开头，港股用hk开头，美股用us开头。 |

**成功响应 (200)**:

| 字段名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `msg` | 字符串 | 是 | 响应消息 |
| `code` | 整数 | 是 | 响应状态码，200 表示成功 |
| `data` | 数组 | 是 | 响应数据 |
| `data[].time` | 整数 | 是 | 时间戳 |
| `data[].date` | 字符串 | 是 | 日期 |
| `data[].inflow` | 实数 | 是 | 流入金额 |
| `data[].outflow` | 实数 | 是 | 流出金额 |

**响应示例**:

```json
{
  "msg": "ok",
  "code": 200,
  "data": []
}
```

---

### <a id="api-55"></a>55. GET IPO新股上市

| 属性 | 值 |
|------|----|
| **路径** | `/api/stock/v1/newIPO` |
| **方法** | `GET` |
| **适用版本** | 按量计费、免费版、个人版、专业版、企业版 |

**请求参数**:

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| `token` | query | string | 否 | token,通过登录获取 |
| `countryCode` | query | string (CHN, HKG, USA) | 否 | 国家/地区代码（CHN：中国，HKG：香港，USA：美国）。 |

**成功响应 (200)**:

| 字段名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `msg` | 字符串 | 是 | 响应消息 |
| `code` | 字符串 | 是 | 代码 |
| `data` | 数组 | 是 | 响应数据 |
| `data[].code` | 字符串 | 是 | 代码 |
| `data[].name` | 字符串 | 是 | 名称 |
| `data[].type` | 字符串 | 是 | 类型(STOCK：股票) |
| `data[].exchangeCode` | 字符串 | 是 | 交易所代码 |
| `data[].countryCode` | 字符串 | 是 | 国家/地区代码 |
| `data[].subscriptionStartDate` | 字符串 | 是 | 申购开始日期 |
| `data[].subscriptionEndDate` | 字符串 | 是 | 申购结束日期 |
| `data[].totalOfferShares` | 整数 | 是 | 发行总数 |
| `data[].subscriptionCode` | 字符串 | 是 | 申购代码(A股) |
| `data[].onlineApplyLimit` | 整数 | 是 | 网上申购上限(股)(A股) |
| `data[].listingDate` | 字符串 | 是 | 上市日期 |
| `data[].offerPriceMin` | 数字 | 是 | 发行价下限 |
| `data[].offerPriceMax` | 数字 | 是 | 发行价上限 |
| `data[].finalPrice` | 数字 | 是 | 最终发行价 |
| `data[].estimatedMarketCap` | 数字 | 是 | 预计市值 |
| `data[].onlineOfferShares` | 整数 | 是 | 网上发行数量 |
| `data[].newShares` | 整数 | 是 | 新股发行数量(A股) |
| `data[].oldShares` | 整数 | 是 | 老股转让数量(A股) |
| `data[].issuePeRatio` | 数字 | 是 | 发行市盈率(A股) |
| `data[].industryPeRatio` | 数字 | 是 | 行业市盈率(A股) |
| `data[].winningRate` | 数字 | 是 | 中签率(%)(A股) |
| `data[].boardLotSize` | 整数 | 是 | 每手股数(港股) |
| `data[].overSubscription` | 数字 | 是 | 超购倍数(港股) |

**响应示例**:

```json
{
  "msg": "ok",
  "code": 200,
  "data": [
    {
      "code": "301583",
      "name": "托伦斯",
      "type": "STOCK",
      "exchangeCode": "XSHE",
      "countryCode": "CHN",
      "subscriptionStartDate": "2026-06-29",
      "subscriptionEndDate": "2026-06-29",
      "totalOfferShares": 46370000,
      "subscriptionCode": "301583",
      "onlineApplyLimit": 9500
    },
    {
      "code": "920136",
      "name": "永励精密",
      "type": "STOCK",
      "exchangeCode": "BJSE",
      "countryCode": "CHN",
      "subscriptionStartDate": "2026-06-24",
      "subscriptionEndDate": "2026-06-24",
      "offerPriceMin": "19.28",
      "offerPriceMax": "19.28",
      "finalPrice": "19.28",
      "totalOfferShares": 20000000,
      "subscriptionCode": "920136",
      "issuePeRatio": "14.99",
      "onlineApplyLimit": 900000
    }
  ]
}
```

---

### <a id="api-56"></a>56. GET 个股股新闻

| 属性 | 值 |
|------|----|
| **路径** | `/api/stock/v1/news` |
| **方法** | `GET` |
| **适用版本** | 按量计费、免费版、个人版、专业版、企业版 |

**请求参数**:

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| `token` | query | string | 否 | token,通过登录获取 |
| `symbol` | query | string | 是 | 股票代码，上证用sh，深证用sz，北证用bj，港股用hk |
| `beginDate` | query | string | 否 | 起始日期。格式“yyyy-mm-dd hh:mm:ss”。 |
| `endDate` | query | string | 否 | 结束日期。格式“yyyy-mm-dd hh:mm:ss”。 |
| `limit` | query | string | 否 | 数量，默认：200。（最大为500） |

**成功响应 (200)**:

| 字段名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `msg` | 字符串 | 是 | 响应消息 |
| `code` | 整数 | 是 | 响应状态码，200 表示成功 |
| `data` | 数组 | 是 | 响应数据 |
| `data[].announcementDate` | 字符串 | 是 | 发布时间 |
| `data[].announcementTime` | 整数 | 是 | 发布时间戳 |
| `data[].title` | 字符串 | 是 | 新闻标题 |
| `data[].summary` | 字符串 | 是 | 新闻摘要 |
| `data[].url` | 字符串 | 是 | 新闻链接 |
| `data[].source` | 字符串 | 是 | 新闻来源 |
| `data[].platform` | 字符串 | 是 | 来源平台 |
| `data[].content` | 数组 | 是 | 正文内容片段 |
| `data[].content[].desc` | 字符串 | 是 | 正文内容 |
| `data[].content[].type` | 字符串 | 是 | 内容类型 |
| `data[].titleMentions` | 数组 | 是 | 标题提及的标的 |
| `data[].bodyMentions` | 数组 | 是 | 正文提及的标的 |

**响应示例**:

```json
{
  "msg": "ok",
  "code": 200,
  "data": [
    {
      "announcementDate": "2026-06-25",
      "announcementTime": 1782316800000,
      "title": "贵州茅台相关资讯标题",
      "summary": "新闻摘要内容",
      "url": "https://example.com/news",
      "source": "新闻来源",
      "platform": "新闻平台",
      "content": [
        {
          "desc": "正文内容片段",
          "type": "text"
        }
      ],
      "titleMentions": [],
      "bodyMentions": []
    }
  ]
}
```

---

### <a id="api-57"></a>57. GET 券商研报

| 属性 | 值 |
|------|----|
| **路径** | `/api/stock/v1/researchReport` |
| **方法** | `GET` |
| **适用版本** | 按量计费、免费版、个人版、专业版、企业版 |

**请求参数**:

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| `token` | query | string | 否 | token,通过登录获取 |
| `symbol` | query | string | 是 | 股票代码，上证用sh，深证用sz，北证用bj |
| `beginDate` | query | string | 否 | 起始日期。格式“yyyy-mm-dd hh:mm:ss”。 |
| `endDate` | query | string | 否 | 结束日期。格式“yyyy-mm-dd hh:mm:ss”。 |
| `limit` | query | string | 否 | 数量，默认：200。（最大为500） |

**成功响应 (200)**:

| 字段名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `code` | 字符串 | 是 | 股票代码 |
| `announcementDate` | 字符串 | 是 | 公告日 |
| `title` | 字符串 | 是 | 研报标题 |
| `summary` | 字符串 | 是 | 研报摘要 |
| `institution` | 字符串 | 是 | 机构 |
| `institutionCode` | 字符串 | 是 | 机构代码 |
| `source` | 字符串 | 是 | 数据来源 |

**响应示例**:

```json
{
          "msg": "ok",
          "code": 200,
          "data": [
                    {
                              "code": "600519",
                              "announcementDate": "2026-06-15 00:00:00",
                              "summary": "　　本报告导读：
　　公司召开年度股东会，肯定市场化改革初始阶段成果。本轮市场化覆盖全产业链、全流程，随着市场需求成为公司经营的核心驱动力，公司发展有望保持稳健态势。
　　投资要点：
　　投资建议：维 持增持评级。维持 2026-2028 年EPS 预测值 66.90元、70.36 元、73.88 元，参考可比公司估值，茅台市场化改革力度较大、业绩确定性较强，同时考虑消费板块流动性较弱，给予公司2026 年26X PE，下调目标价至1739.4 元。
　　公司召开年度股东会，系统阐释改革举措。6 月11 日贵州茅台召开股东会，期间对市场化转型的多个事项进行回应，在1 月13 日发布的《2026 年贵州茅台酒市场化运营方案》的基础上进一步阐释本次改革的想法和举措，肯定改革初始阶段成果。市场关注的价格调整节奏方面，核心是随行就市、相对平稳，观察后续供需变化。
　　全面向C，i 茅台提升触达能力。全面向C 的背景下，茅台重塑渠道体系，形成线上线下各司其职的渠道网络，其中自营渠道体系担当市场的平衡器、稳定器，稳定平衡市场秩序，防止过度炒作；社会渠道体系担当放大器、转化器，做好客群的维护转化，提供品牌服务和消费者体验。之前市场担忧自营对传统经销形成替代，公司对此回应，“茅台与各类渠道商从来都不是此消彼长的竞争关系，更不是相互替代的取舍关系，而是各有优势合作共赢的协同伙伴关系，是紧密相连的利益共同体、命运共同体”。线上化承担本轮改革的高效触达环节，截至5 月31 日，i 茅台2026 年新增注册用户数约1667万人、累计注册用户9615 万人，平均月活约956 万人，成交订单约713 万人次，用户规模较26Q1 进一步增加。据我们测算，根据成交订单数、单均收入、投放节奏等参数假设，26Q2 i 茅台营收有望延续快速增长态势，持续贡献业绩增量（后附测算过程）。
　　多元并进，全流程市场化。品牌矩阵、市场建设方面转型同步推进，系列酒以“稳”为主，夯实当前规模地位；海外市场主动调整，由产品出口向品牌出海跨越。过去白酒产业的改革集中在营销和渠道层面，茅台强调本次市场化不止针对销售端，是覆盖全产业链、全流程的市场化，包括产品端、渠道端、服务端、终端和推广端。随着市场需求成为公司经营核心驱动力，业务体系将迈向全面数字化，以适应新的发展逻辑，公司有望保持稳健态势，夯实龙头优势。
　　风险提示：转型改革效果弱于预期、批价大幅回调、食品安全风险",
                              "title": "贵州茅台(600519)更新报告：C端引领 全流程市场化",
                              "institution": "国泰海通证券",
                              "institutionCode": "2726",
                              "source": "tencent"
                    },
                    {
                              "code": "600519",
                              "announcementDate": "2026-06-14 00:00:00",
                              "summary": "　　贵州茅台召开2025 年度股东大会，陈华董事长首次以董事长身份主持。公司明确建立"随行就市、相对平稳、量价平衡"的动态价格调整机制，将价格机制从"被动应对"提升至"主动管控"。本轮市场化改革聚焦以消费者为中心，自营做平衡器、社会做转化器，管理层走访调研，合作伙伴对改革有信心、对成效较为认可。i 茅台成为"全面向C"核心抓手，系列酒2026 年目标站稳200 亿阵营、构建"2+N"产品体系。
　　市场需求驱动，价格随行就市动态调节机制。近期公司召开2025 年度股东会，陈华董事长首次以董事长身份主持。公司明确建立"随行就市、相对平稳、量价平衡"的动态价格调整机制，以市场需求为驱动，动态监测供给、消费、库存及终端动销，结合不同产品差异科学研判。陈华董事长强调价格不能大起大落、量价必须平衡，决策高度统一管控，关于价格的网络非官方信息均不属实。这是公司首次将价格机制从"被动应对"提升至"主动管控"的战略高度，反映出公司对市场秩序的把控能力增强。
　　自营+社会渠道双轮驱动，合作伙伴对改革有信心、对成效认可。本轮改革聚焦以消费者为中心，是产品体系、渠道生态、商业模式、供应链组织的全面转型升级，与以往单纯聚焦渠道有本质不同。自营渠道担当市场平衡器和稳定器，防止过度炒作；社会渠道担当放大器和转化器，主动触达C端、深耕品质文化传播。公司管理层过去一个多月走访粤浙湘甘川五省，合作伙伴对改革有信心、对成效较为认可，渠道层面接受度高于市场预期。
　　i 茅台成为"全面向C"核心抓手，系列酒"2+N"产品体系清晰。i 茅台已是公司直接触达C 端最重要的数字化资产，投放坚持供需适配、量价平衡，截至5 月31 日累计注册9615 万人/月活约956 万/年内新增注册约1667 万/累计成交订单约713 万人次，运营围绕商品、用户、内容、数据、技术持续升级。系列酒2026 年目标站稳200 亿阵营，构建"2+N"产品体系：1935主攻次高端、王子酒深耕大众，N 围绕汉酱、贵州大曲、迎宾酒做特色，渠道精准管理，以"不竭泽而渔、不唯指标"的战略定力科学处理发展与稳定关系。
　　国际化从产品出口向品牌出海跨越，品牌做长红不做网红。国际化已编制2026-2030 年转型方案，从渠道驱动转向消费者驱动，围绕品牌、产品、价格、渠道、政策、合规六大体系推进，国际市场被定位为高质量发展新增长极。年轻化方面，公司明确"做长红品牌而非网红品牌"，茅台冰淇淋、酱香拿铁、巧克力等异业逐步收缩，未来联名将非常谨慎，i 茅台春节问卷153 万用户中45 岁以下占比7 成以上，年轻化已现真实抓手。
　　投资建议：以消费者为锚，改革红利徐徐释放，维持"强烈推荐"。本次股东大会，公司在价格机制、渠道生态、消费者运营、国际化等维度给出了更清晰的战略表达。目前改革已经初现成效、合作伙伴认可改革，自营+社会双渠道生态持续重塑。股东回报角度，三年分红规划已实施两年、注销式股份回购已开展，市值管理连续性、稳定性、可持续性有保障，目前对应4.2%股东回报率。维持26-28 年EPS 预测为67.91、72.01、75.76 元，当前对应26 年19X PE,重申“强烈推荐”评级。
　　风险提示：政策影响超预期、外资流出、税率上升、宏观经济影响、提价传导不通畅等",
                              "title": "贵州茅台(600519)：以消费者为锚 改革红利徐徐释放",
                              "institution": "招商证券",
                              "institutionCode": "2921",
                              "source": "tencent"
                    }
          ]
}
```

---

### <a id="api-58"></a>58. GET 企业管理层薪酬及持股

| 属性 | 值 |
|------|----|
| **路径** | `/api/stock/v1/rewards` |
| **方法** | `GET` |
| **适用版本** | 按量计费、免费版、个人版、专业版、企业版 |

**请求参数**:

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| `token` | query | string | 否 | token,通过登录获取 |
| `symbol` | query | string | 是 | 股票代码，上证用sh开头，深证用sz开头，北证用bj开头，港股用hk开头，美股用us开头。 |

**成功响应 (200)**:

| 字段名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `msg` | 字符串 | 是 | 响应消息 |
| `code` | 整数 | 是 | 响应状态码，200 表示成功 |
| `data` | 数组 | 是 | 响应数据 |
| `data[].name` | 字符串 | 是 | 姓名 |
| `data[].title` | 字符串 | 是 | 职务 |
| `data[].compensation` | 数字 | 是 | 税前薪酬 |
| `data[].shareholding` | 数字 | 是 | 持股数量 |

**响应示例**:

```json
{
  "msg": "ok",
  "code": 200,
  "data": [
    {
      "name": "张德芹",
      "title": "党委书记,董事长,董事",
      "compensation": 1210700,
      "shareholding": 0
    },
    {
      "name": "郭田勇",
      "title": "独立董事",
      "compensation": 200000,
      "shareholding": 0
    }
  ]
}
```

---

### <a id="api-59"></a>59. GET 历史股本

| 属性 | 值 |
|------|----|
| **路径** | `/api/stock/v1/shares` |
| **方法** | `GET` |
| **适用版本** | 按量计费、免费版、个人版、专业版、企业版 |

**请求参数**:

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| `token` | query | string | 否 | token,通过登录获取 |
| `symbol` | query | string | 是 | 股票代码，上证用sh开头，深证用sz开头，北证用bj开头，港股用hk开头，美股用us开头。 |

**成功响应 (200)**:

| 字段名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `msg` | 字符串 | 是 | 响应消息 |
| `code` | 整数 | 是 | 响应状态码，200 表示成功 |
| `data` | 数组 | 是 | 响应数据 |
| `data[].date` | 字符串 | 是 | 日期(yyyy-MM-dd) |
| `data[].totalShares` | 整数 | 是 | 总股本 |
| `data[].floatingShares` | 整数 | 是 | 流通股本 |
| `data[].limitedShares` | 整数 | 是 | 限售股本 |
| `data[].changeReason` | 字符串 | 是 | 变动原因 |
| `data[].time` | 整数 | 是 | 时间戳 |

**响应示例**:

```json
{
  "msg": "ok",
  "code": 200,
  "data": [
    {
      "date": "2026-05-28",
      "totalShares": "1250081601",
      "floatingShares": "1250081601",
      "limitedShares": "0",
      "changeReason": "回购"
    },
    {
      "date": "2025-09-01",
      "totalShares": "1252270215",
      "floatingShares": "1252270215",
      "limitedShares": "0",
      "changeReason": "回购"
    }
  ]
}
```

---

### <a id="api-60"></a>60. GET 股票排行

| 属性 | 值 |
|------|----|
| **路径** | `/api/stock/v1/sort` |
| **方法** | `GET` |
| **适用版本** | 按量计费、专业版、企业版 |

**请求参数**:

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| `token` | query | string | 否 | token,通过登录获取 |
| `countryCode` | query | string (CHN, HKG, USA) | 否 | 国家/地区代码，和交易所，股票市场三选一。（CHN：中国大陆，HKG：中国香港，USA：美国）） |
| `exchangeCode` | query | string (XSHG, XSHE, BJSE, XHKG, XNAS, XNYS, AMEX) | 否 | 交易所代码，和国家/地区，股票市场三选一。（XSHG：上交所，XSHE：深交所，BJSE：北交所，XHKG：香港交易所，XNAS：纳斯达克，XNYS：纽约证卷交易所，AMEX：美国证卷交易所） |
| `market` | query | string (cn_hs, cn_hs_a, cn_hs_m, cn_hsj, cn_cyb, cn_kcb, cn_bjs, hk_main, hk_cyb, hk_gq, hk_hc, us_tech, us_china, us_star) | 否 | 股票市场，和国家/地区，交易所三选一。
（cn_hs：沪深所有，cn_hs_a：沪深A股，cn_hs_m：沪深主板，cn_hsj：沪深京所有，cn_cyb：创业板，cn_kcb：科创板，cn_bjs：北交所，us_tech：美股科技股，us_china：美股中概股，us_star：美股明星股,hk_main：港股主板，hk_cyb：港股创业板，hk_gq：港股国企股，hk_hc：港股红筹股）。 |
| `sort` | query | string (price, change, changeRate, volume, amount, turnover, pe_ttm, pe_dyn, pe_static, pb, eps, committee, circulationValue, marketValue, circulationShares, totalShares, amplitude, open, high, low, preClose) | 否 | 排序方式。
（price：价格，change：涨跌额，changeRate：涨跌幅，volume：成交量，amount：成交额，turnover：换手率，pe_ttm：ttm市盈率，pe_dyn：动态市盈率，pe_static：静态市盈率，
                    pb：市净率，eps：每股收益，committee：委比，circulationValue：流通市值，marketValue：总市值，circulationShares：流通股本，totalShares：总股本，amplitude：振幅，open：开盘价，high：最高价，low：最低价，preClose：昨收） |
| `order` | query | string (ASC, DESC) | 是 | 顺序：ASC 表升序，DESC 表降序（默认DESC） |
| `page` | query | string | 否 | 第几页，每页100行数据 |
| `format` | query | string (json, csv) | 否 | 格式,支持json格式和csv格式（默认json格式） |

**成功响应 (200)**:

| 字段名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `msg` | 字符串 | 是 | 响应消息 |
| `code` | 字符串 | 是 | 代码 |
| `data` | 对象 | 是 | 响应数据 |
| `data.pageNum` | 整数 | 是 |  |
| `data.pageTotal` | 整数 | 是 |  |
| `data.countTotal` | 整数 | 是 |  |
| `data.list` | 数组 | 是 |  |
| `data.list[].code` | 字符串 | 是 | 代码 |
| `data.list[].name` | 字符串 | 是 | 名称 |
| `data.list[].type` | 字符串 | 是 | 类型(STOCK：股票，INDEX：指数，FUND：基金，FOREX：外汇，CRYPTO：加密货币) |
| `data.list[].exchangeCode` | 字符串 | 是 | 交易所代码。详见交易所清单接口。 |
| `data.list[].countryCode` | 字符串 | 是 | 国家/地区代码。详见国家/地区清单接口。 |
| `data.list[].timestamp` | 整数 | 是 |  |
| `data.list[].localDate` | 字符串 | 是 | 更新时间。 |
| `data.list[].price` | 字符串 | 是 | 价格 |
| `data.list[].open` | 字符串 | 是 | 开盘价 |
| `data.list[].high` | 字符串 | 是 | 最高价 |
| `data.list[].low` | 字符串 | 是 | 最低价 |
| `data.list[].preClose` | 字符串 | 是 | 收盘价 |
| `data.list[].volume` | 字符串 | 是 | 成交量 |
| `data.list[].amount` | 字符串 | 是 | 成交额 |
| `data.list[].change` | 字符串 | 是 | 涨跌额 |
| `data.list[].changeRate` | 字符串 | 是 | 涨跌幅 |
| `data.list[].bidPx1` | 实数 | 是 | 买一价 |
| `data.list[].bidPx2` | 实数 | 是 | 买二价 |
| `data.list[].bidPx3` | 实数 | 是 | 买三价 |
| `data.list[].bidPx4` | 实数 | 是 | 买四价 |
| `data.list[].bidPx5` | 实数 | 是 | 买五价 |
| `data.list[].bidVol1` | 整数 | 是 | 买一量 |
| `data.list[].bidVol2` | 整数 | 是 | 买二量 |
| `data.list[].bidVol3` | 整数 | 是 | 买三量 |
| `data.list[].bidVol4` | 整数 | 是 | 买四量 |
| `data.list[].bidVol5` | 整数 | 是 | 买五量 |
| `data.list[].askPx1` | 实数 | 是 | 卖一价 |
| `data.list[].askPx2` | 实数 | 是 | 卖二价 |
| `data.list[].askPx3` | 实数 | 是 | 卖三价 |
| `data.list[].askPx4` | 实数 | 是 | 卖四价 |
| `data.list[].askPx5` | 实数 | 是 | 卖五价 |
| `data.list[].askVol1` | 整数 | 是 | 卖一量 |
| `data.list[].askVol2` | 整数 | 是 | 卖二量 |
| `data.list[].askVol3` | 整数 | 是 | 卖三量 |
| `data.list[].askVol4` | 整数 | 是 | 卖四量 |
| `data.list[].askVol5` | 整数 | 是 | 卖五量 |
| `data.list[].mktCap` | 字符串 | 是 | 总市值 |
| `data.list[].floatCap` | 字符串 | 是 | 流通市值 |
| `data.list[].totShr` | 字符串 | 是 | 总股本 |
| `data.list[].floatShr` | 字符串 | 是 | 流通股本 |
| `data.list[].ordImbRatio` | 字符串 | 是 | 委比 |
| `data.list[].pb` | 字符串 | 是 | 市净率 |
| `data.list[].volRatio` | 字符串 | 是 | 量比 |
| `data.list[].turnover` | 字符串 | 是 | 换手率 |
| `data.list[].pe_ttm` | 字符串 | 是 | TTM市盈率 |
| `data.list[].pe_dyn` | 字符串 | 是 | 动态市盈率 |
| `data.list[].pe_static` | 字符串 | 是 | 静态市盈率 |
| `data.list[].amplitude` | 字符串 | 是 | 振幅 |
| `data.list[].highLimit` | 字符串 | 是 | 涨停价格 |
| `data.list[].lowLimit` | 字符串 | 是 | 跌停价格 |
| `data.chineseName` | 字符串 | 是 | 中文名称（美股）。 |
| `data.activeSellVol` | 整数 | 是 | 内盘(主动卖出总量) |
| `data.activeBuyVol` | 整数 | 是 | 外盘(主动买入总量) |
| `data.eps` | 字符串 | 是 | 每股收益 |
| `data.bps` | 字符串 | 是 | 每股净资产 |
| `data.avgPrice` | 字符串 | 是 | 股息 |
| `data.dividend` | 字符串 | 是 | 股息率 |
| `data.dividendYield` | 字符串 | 是 | 均价 |

**响应示例**:

```json
{
  "msg": "ok",
  "code": 200,
  "data": {
    "pageNum": 1,
    "pageTotal": 105,
    "countTotal": 5210,
    "list": [
      {
        "code": "300228",
        "name": "富瑞特装",
        "type": "STOCK",
        "exchangeCode": "XSHE",
        "countryCode": "CHN",
        "timestamp": 1782350352000,
        "localDate": "2026-06-25 09:19:12",
        "price": "9.23",
        "open": "0",
        "high": "0",
        "low": "0",
        "preClose": "7.69",
        "volume": "0",
        "amount": "0",
        "change": "1.54",
        "changeRate": "20.03",
        "bidPx1": "9.23",
        "bidPx2": "0",
        "bidPx3": "0",
        "bidPx4": "0",
        "bidPx5": "0",
        "bidVol1": 3103800,
        "bidVol2": 0,
        "bidVol3": 0,
        "bidVol4": 0,
        "bidVol5": 0,
        "askPx1": "9.23",
        "askPx2": "0",
        "askPx3": "0",
        "askPx4": "0",
        "askPx5": "0",
        "askVol1": 3103800,
        "askVol2": 1288000,
        "askVol3": 0,
        "askVol4": 0,
        "askVol5": 0,
        "mktCap": "5514000000",
        "floatCap": "5159000000",
        "totShr": "597425549",
        "floatShr": "558904049",
        "ordImbRatio": 17.18,
        "pb": 2.23,
        "volRatio": 0,
        "turnover": 0,
        "pe_ttm": 22.25,
        "pe_dyn": 24.19,
        "pe_static": 22.87,
        "amplitude": 0,
        "highLimit": "9.23",
        "lowLimit": "6.15"
      },
      {
        "code": "300384",
        "name": "三联虹普",
        "type": "STOCK",
        "exchangeCode": "XSHE",
        "countryCode": "CHN",
        "timestamp": 1782350352000,
        "localDate": "2026-06-25 09:19:12",
        "price": "14.39",
        "open": "0",
        "high": "0",
        "low": "0",
        "preClose": "11.99",
        "volume": "0",
        "amount": "0",
        "change": "2.4",
        "changeRate": "20.02",
        "bidPx1": "14.39",
        "bidPx2": "0",
        "bidPx3": "0",
        "bidPx4": "0",
        "bidPx5": "0",
        "bidVol1": 444400,
        "bidVol2": 2300,
        "bidVol3": 0,
        "bidVol4": 0,
        "bidVol5": 0,
        "askPx1": "14.39",
        "askPx2": "0",
        "askPx3": "0",
        "askPx4": "0",
        "askPx5": "0",
        "askVol1": 444400,
        "askVol2": 0,
        "askVol3": 0,
        "askVol4": 0,
        "askVol5": 0,
        "mktCap": "4591000000",
        "floatCap": "3167000000",
        "totShr": "319007265",
        "floatShr": "220113489",
        "ordImbRatio": -0.26,
        "pb": 1.62,
        "volRatio": 0,
        "turnover": 0,
        "pe_ttm": 24.32,
        "pe_dyn": 25.32,
        "pe_static": 20.52,
        "amplitude": 0,
        "highLimit": "14.39",
        "lowLimit": "9.59"
      }
    ]
  }
}
```

---

### <a id="api-61"></a>61. GET 股票清单

| 属性 | 值 |
|------|----|
| **路径** | `/api/stock/v1/stockList` |
| **方法** | `GET` |
| **适用版本** | 按量计费、免费版、个人版、专业版、企业版 |

**请求参数**:

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| `token` | query | string | 否 | token,通过登录获取 |
| `countryCode` | query | string (CHN, HKG, USA) | 否 | 国家/地区代码，和交易所，股票市场三选一。（CHN：中国大陆，HKG：中国香港，USA：美国）） |
| `exchangeCode` | query | string (XSHG, XSHE, BJSE, XHKG, XNAS, XNYS, AMEX) | 否 | 交易所代码，和国家/地区，股票市场三选一。（XSHG：上交所，XSHE：深交所，BJSE：北交所，XHKG：香港交易所，XNAS：纳斯达克，XNYS：纽约证卷交易所，AMEX：美国证卷交易所） |
| `market` | query | string (cn_hs, cn_hs_a, cn_hs_m, cn_hsj, cn_cyb, cn_kcb, cn_bjs, hk_main, hk_cyb, hk_gq, hk_hc, us_tech, us_china, us_star) | 否 | 股票市场，和国家/地区，交易所三选一。
（cn_hs：沪深所有，cn_hs_a：沪深A股，cn_hs_m：沪深主板，cn_hsj：沪深京所有，cn_cyb：创业板，cn_kcb：科创板，cn_bjs：北交所，us_tech：美股科技股，us_china：美股中概股，us_star：美股明星股,hk_main：港股主板，hk_cyb：港股创业板，hk_gq：港股国企股，hk_hc：港股红筹股）。 |
| `format` | query | string (json, csv) | 否 | 格式,支持json格式和csv格式（默认json格式） |

**成功响应 (200)**:

| 字段名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `msg` | 字符串 | 是 | 响应消息 |
| `code` | 字符串 | 是 | 代码 |
| `data` | 数组 | 是 | 响应数据 |
| `data[].code` | 字符串 | 是 | 代码 |
| `data[].name` | 字符串 | 是 | 名称 |
| `data[].type` | 字符串 | 是 | 类型(STOCK：股票，INDEX：指数，FUND：基金，FOREX：外汇，CRYPTO：加密货币) |
| `data[].exchangeCode` | 字符串 | 是 | 交易所代码。详见交易所清单接口。 |
| `data[].countryCode` | 字符串 | 是 | 国家/地区代码。详见国家/地区清单接口。 |
| `data[].chineseName` | 字符串 | 是 | 中文名称（美股）。 |

**响应示例**:

```json
{
  "msg": "ok",
  "code": 200,
  "data": [
    {
      "code": "301630",
      "name": "同宇新材",
      "type": "STOCK",
      "exchangeCode": "XSHE",
      "countryCode": "CHN"
    },
    {
      "code": "300931",
      "name": "通用电梯",
      "type": "STOCK",
      "exchangeCode": "XSHE",
      "countryCode": "CHN"
    }
  ]
}
```

---

### <a id="api-62"></a>62. GET Top10流动股东

| 属性 | 值 |
|------|----|
| **路径** | `/api/stock/v1/top10FloatShareholders` |
| **方法** | `GET` |
| **适用版本** | 按量计费、免费版、个人版、专业版、企业版 |

**请求参数**:

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| `token` | query | string | 否 | token,通过登录获取 |
| `symbol` | query | string | 是 | 股票代码，上证用sh开头，深证用sz开头，北证用bj开头，港股用hk开头，美股用us开头。 |

**成功响应 (200)**:

| 字段名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `msg` | 字符串 | 是 | 响应消息 |
| `code` | 整数 | 是 | 响应状态码，200 表示成功 |
| `data` | 对象 | 是 | 响应数据 |
| `data.shareholders` | 数组 | 是 |  |
| `data.shareholders[].announcementDate` | 字符串 | 是 |  |
| `data.shareholders[].reportDate` | 字符串 | 是 |  |
| `data.shareholders[].holderName` | 字符串 | 是 |  |
| `data.shareholders[].holdAmount` | 整数 | 是 |  |
| `data.shareholders[].holdRatio` | 实数 | 是 |  |
| `data.shareholders[].holdFloatRatio` | 实数 | 是 |  |
| `data.shareholders[].holdChange` | 整数 | 是 |  |
| `data.shareholders[].holderType` | 字符串 | 是 |  |
| `data.floatShareholders` | 数组 | 是 |  |
| `data.floatShareholders[].announcementDate` | 字符串 | 是 |  |
| `data.floatShareholders[].reportDate` | 字符串 | 是 |  |
| `data.floatShareholders[].holderName` | 字符串 | 是 |  |
| `data.floatShareholders[].holdAmount` | 整数 | 是 |  |
| `data.floatShareholders[].holdRatio` | 实数 | 是 |  |
| `data.floatShareholders[].holdFloatRatio` | 实数 | 是 |  |
| `data.floatShareholders[].holdChange` | 整数 | 是 |  |
| `data.floatShareholders[].holderType` | 字符串 | 是 |  |
| `data.holders` | 数组 | 是 | 前十大股东 |
| `data.floatHolders` | 数组 | 是 | 前十大流通股东 |
| `data.name` | 字符串 | 是 | 股东名称 |
| `data.ratio` | 实数 | 是 | 持股比例(%) |
| `data.shareCount` | 实数 | 是 | 持股数量 |

**响应示例**:

```json
{
  "msg": "ok",
  "code": 200,
  "data": {
    "shareholders": [
      {
        "announcementDate": "2026-04-25",
        "reportDate": "2026-03-31",
        "holderName": "中国工商银行股份有限公司-华泰柏瑞沪深300交易型开放式指数证券投资基金",
        "holdAmount": 5038480,
        "holdRatio": 0.4023,
        "holdFloatRatio": 0.4023,
        "holdChange": -5286170,
        "holderType": "开放式投资基金"
      },
      {
        "announcementDate": "2026-04-25",
        "reportDate": "2026-03-31",
        "holderName": "中国贵州茅台酒厂(集团)有限责任公司",
        "holdAmount": 681283000,
        "holdRatio": 54.4038,
        "holdFloatRatio": 54.4038,
        "holderType": "一般企业"
      }
    ],
    "floatShareholders": [
      {
        "announcementDate": "2026-04-25",
        "reportDate": "2026-03-31",
        "holderName": "中国工商银行股份有限公司-华泰柏瑞沪深300交易型开放式指数证券投资基金",
        "holdAmount": 5038482,
        "holdRatio": 0.4023,
        "holdFloatRatio": 0.4023,
        "holdChange": -5286168,
        "holderType": "开放式投资基金"
      },
      {
        "announcementDate": "2026-04-25",
        "reportDate": "2026-03-31",
        "holderName": "香港中央结算有限公司",
        "holdAmount": 58733069,
        "holdRatio": 4.6901,
        "holdFloatRatio": 4.6901,
        "holdChange": 3684225,
        "holderType": "一般企业"
      }
    ]
  }
}
```

---

### <a id="api-63"></a>63. GET Top10股东/流动股东

| 属性 | 值 |
|------|----|
| **路径** | `/api/stock/v1/top10holders` |
| **方法** | `GET` |
| **适用版本** | 按量计费、免费版、个人版、专业版、企业版 |

**请求参数**:

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| `token` | query | string | 否 | token,通过登录获取 |
| `symbol` | query | string | 是 | 股票代码，上证用sh开头，深证用sz开头，北证用bj开头，港股用hk开头，美股用us开头。 |

**成功响应 (200)**:

| 字段名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `msg` | 字符串 | 是 | 响应消息 |
| `code` | 整数 | 是 | 响应状态码，200 表示成功 |
| `data` | 对象 | 是 | 响应数据 |
| `data.holders` | 数组 | 是 | 前十大股东 |
| `data.holders[].name` | 字符串 | 是 | 股东名称 |
| `data.holders[].ratio` | 实数 | 是 | 持股比例(%) |
| `data.holders[].shareCount` | 实数 | 是 | 持股数量 |
| `data.floatHolders` | 数组 | 是 | 前十大流通股东 |
| `data.floatHolders[].name` | 字符串 | 是 | 股东名称 |
| `data.floatHolders[].ratio` | 实数 | 是 | 持股比例(%) |
| `data.floatHolders[].shareCount` | 实数 | 是 | 持股数量 |

**响应示例**:

```json
{
  "msg": "ok",
  "code": 200,
  "data": {
    "holders": [
      {
        "name": "中国贵州茅台酒厂(集团)有限责任公司",
        "ratio": 54.18,
        "shareCount": 680939055
      },
      {
        "name": "香港中央结算有限公司",
        "ratio": 6.35,
        "shareCount": 79798025
      },
      {
        "name": "贵州省国有资本运营有限责任公司",
        "ratio": 4.54,
        "shareCount": 56996777
      }
    ],
    "floatHolders": [
      {
        "name": "中国贵州茅台酒厂(集团)有限责任公司",
        "ratio": 54.18,
        "shareCount": 680939055
      },
      {
        "name": "香港中央结算有限公司",
        "ratio": 6.35,
        "shareCount": 79798025
      },
      {
        "name": "贵州省国有资本运营有限责任公司",
        "ratio": 4.54,
        "shareCount": 56996777
      }
    ]
  }
}
```

---

### <a id="api-64"></a>64. GET Top10股东/流动股东

| 属性 | 值 |
|------|----|
| **路径** | `/api/stock/v1/top10Shareholders` |
| **方法** | `GET` |
| **适用版本** | 按量计费、免费版、个人版、专业版、企业版 |

**请求参数**:

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| `token` | query | string | 否 | token,通过登录获取 |
| `symbol` | query | string | 是 | 股票代码，上证用sh开头，深证用sz开头，北证用bj开头，港股用hk开头，美股用us开头。 |

**成功响应 (200)**:

| 字段名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `msg` | 字符串 | 是 | 响应消息 |
| `code` | 整数 | 是 | 响应状态码，200 表示成功 |
| `data` | 对象 | 是 | 响应数据 |
| `data.shareholders` | 数组 | 是 |  |
| `data.shareholders[].announcementDate` | 字符串 | 是 |  |
| `data.shareholders[].reportDate` | 字符串 | 是 |  |
| `data.shareholders[].holderName` | 字符串 | 是 |  |
| `data.shareholders[].holdAmount` | 整数 | 是 |  |
| `data.shareholders[].holdRatio` | 实数 | 是 |  |
| `data.shareholders[].holdFloatRatio` | 实数 | 是 |  |
| `data.shareholders[].holdChange` | 整数 | 是 |  |
| `data.shareholders[].holderType` | 字符串 | 是 |  |
| `data.floatShareholders` | 数组 | 是 |  |
| `data.floatShareholders[].announcementDate` | 字符串 | 是 |  |
| `data.floatShareholders[].reportDate` | 字符串 | 是 |  |
| `data.floatShareholders[].holderName` | 字符串 | 是 |  |
| `data.floatShareholders[].holdAmount` | 整数 | 是 |  |
| `data.floatShareholders[].holdRatio` | 实数 | 是 |  |
| `data.floatShareholders[].holdFloatRatio` | 实数 | 是 |  |
| `data.floatShareholders[].holdChange` | 整数 | 是 |  |
| `data.floatShareholders[].holderType` | 字符串 | 是 |  |
| `data.holders` | 数组 | 是 | 前十大股东 |
| `data.floatHolders` | 数组 | 是 | 前十大流通股东 |
| `data.name` | 字符串 | 是 | 股东名称 |
| `data.ratio` | 实数 | 是 | 持股比例(%) |
| `data.shareCount` | 实数 | 是 | 持股数量 |

**响应示例**:

```json
{
  "msg": "ok",
  "code": 200,
  "data": {
    "shareholders": [
      {
        "announcementDate": "2026-04-25",
        "reportDate": "2026-03-31",
        "holderName": "中国工商银行股份有限公司-华泰柏瑞沪深300交易型开放式指数证券投资基金",
        "holdAmount": 5038480,
        "holdRatio": 0.4023,
        "holdFloatRatio": 0.4023,
        "holdChange": -5286170,
        "holderType": "开放式投资基金"
      },
      {
        "announcementDate": "2026-04-25",
        "reportDate": "2026-03-31",
        "holderName": "中国贵州茅台酒厂(集团)有限责任公司",
        "holdAmount": 681283000,
        "holdRatio": 54.4038,
        "holdFloatRatio": 54.4038,
        "holderType": "一般企业"
      }
    ],
    "floatShareholders": [
      {
        "announcementDate": "2026-04-25",
        "reportDate": "2026-03-31",
        "holderName": "中国工商银行股份有限公司-华泰柏瑞沪深300交易型开放式指数证券投资基金",
        "holdAmount": 5038482,
        "holdRatio": 0.4023,
        "holdFloatRatio": 0.4023,
        "holdChange": -5286168,
        "holderType": "开放式投资基金"
      },
      {
        "announcementDate": "2026-04-25",
        "reportDate": "2026-03-31",
        "holderName": "香港中央结算有限公司",
        "holdAmount": 58733069,
        "holdRatio": 4.6901,
        "holdFloatRatio": 4.6901,
        "holdChange": 3684225,
        "holderType": "一般企业"
      }
    ]
  }
}
```

---

### <a id="api-65"></a>65. GET 股票K线

| 属性 | 值 |
|------|----|
| **路径** | `/api/stock/v2/kline` |
| **方法** | `GET` |
| **描述** | 目前1min，5min，10min，30min，60min数字只支持A股不复权数据。 |
| **适用版本** | 按量计费、免费版（不含分钟级数据）、个人版（不含分钟级数据）、专业版、企业版 |

**请求参数**:

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| `token` | query | string | 否 | token,通过登录获取 |
| `symbol` | query | string | 是 | 股票代码，上证用sh开头，深证用sz开头，北证用bj开头，港股用hk开头，美股用us开头。 |
| `type` | query | string (day, day5, 1min, 5min, 10min, 15min, 20min, 30min, 60min, d1, w1, m1, y1) | 是 | k线类型， day：当日1分钟，day5：最近5个交易日1分钟，5min：5分钟K线，10min：10分钟K线，15min：15分钟K线，30min：30分钟K线，60min：60分钟K线，d1：日K，w1：周K，m1：月K，y1：年K。 |
| `beginDate` | query | string | 否 | 起始日期。格式“yyyy-mm-dd hh:mm:ss”。 |
| `endDate` | query | string | 否 | 结束日期。格式“yyyy-mm-dd hh:mm:ss”。 |
| `order` | query | string (ASC, DESC) | 否 | 顺序：ASC 表升序从小到大排序，DESC 表降序从大到小排序（默认在不输入时间为默认倒序，只输入开始时间强制为升序，只输入结束时间强制为降序，同时输入开始时间和结束时间为默认为倒序） |
| `limit` | query | string | 否 | 数量，默认：1000。（最大为2000） |
| `fq` | query | string (bfq, qfq) | 否 | 复权：默认不复权。（fq 表不复权，qfq 表示前复权） |
| `format` | query | string (json, csv) | 否 | 格式,支持json格式和csv格式（默认json格式） |

**成功响应 (200)**:

| 字段名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `msg` | 字符串 | 是 | 响应消息 |
| `code` | 字符串 | 是 | 代码 |
| `data` | 数组 | 是 | 响应数据 |
| `data[].date` | 字符串 | 是 | 更新时间 |
| `data[].close` | 字符串 | 是 | 收盘价 |
| `data[].open` | 字符串 | 是 | 开盘价格 |
| `data[].high` | 字符串 | 是 | 最高价 |
| `data[].low` | 字符串 | 是 | 最低价 |
| `data[].preClose` | 字符串 | 是 | 昨收 |
| `data[].volume` | 字符串 | 是 | 成交量 |
| `data[].amount` | 字符串 | 是 | 成交额 |
| `data[].time` | 整数 | 是 | 时间戳(毫秒) |

**响应示例**:

```json
{
  "msg": "ok",
  "code": 200,
  "data": [
    {
      "date": "2026-06-25",
      "close": "1207.7",
      "open": "0",
      "high": "0",
      "low": "0",
      "preClose": "1207.68",
      "volume": "0",
      "amount": "0"
    },
    {
      "date": "2026-06-24",
      "close": "1207.68",
      "open": "1222.65",
      "high": "1241.87",
      "low": "1207.51",
      "preClose": "1222.45",
      "volume": "4533500",
      "amount": "5516574500"
    }
  ]
}
```

---

### <a id="api-66"></a>66. GET 实时行情

| 属性 | 值 |
|------|----|
| **路径** | `/api/stock/v2/realtime` |
| **方法** | `GET` |
| **适用版本** | 按量计费、专业版、企业版 |

**请求参数**:

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| `token` | query | string | 否 | token,通过登录获取 |
| `symbol` | query | string | 是 | 股票代码，支持多支股票用英文逗号隔开（一次可获取20支股票），上证用sh开头，深证用sz开头，北证用bj开头，港股用hk开头，美股用us开头。 |
| `format` | query | string (json, csv) | 否 | 格式,支持json格式和csv格式（默认json格式） |

**成功响应 (200)**:

| 字段名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `msg` | 字符串 | 是 | 响应消息 |
| `code` | 字符串 | 是 | 代码 |
| `data` | 数组 | 是 | 响应数据 |
| `data[].code` | 字符串 | 是 | 代码 |
| `data[].name` | 字符串 | 是 | 名称 |
| `data[].type` | 字符串 | 是 | 类型(STOCK：股票，INDEX：指数，FUND：基金，FOREX：外汇，CRYPTO：加密货币) |
| `data[].exchangeCode` | 字符串 | 是 | 交易所代码。详见交易所清单接口。 |
| `data[].countryCode` | 字符串 | 是 | 国家/地区代码。详见国家/地区清单接口。 |
| `data[].timestamp` | 整数 | 是 |  |
| `data[].updateTime` | 整数 | 是 |  |
| `data[].localDate` | 字符串 | 是 | 更新时间。 |
| `data[].price` | 字符串 | 是 | 价格 |
| `data[].open` | 字符串 | 是 | 开盘价 |
| `data[].high` | 字符串 | 是 | 最高价 |
| `data[].low` | 字符串 | 是 | 最低价 |
| `data[].preClose` | 字符串 | 是 | 收盘价 |
| `data[].volume` | 字符串 | 是 | 成交量 |
| `data[].amount` | 字符串 | 是 | 成交额 |
| `data[].change` | 字符串 | 是 | 涨跌额 |
| `data[].changeRate` | 字符串 | 是 | 涨跌幅 |
| `data[].bidPx1` | 实数 | 是 | 买一价 |
| `data[].bidPx2` | 实数 | 是 | 买二价 |
| `data[].bidPx3` | 实数 | 是 | 买三价 |
| `data[].bidPx4` | 实数 | 是 | 买四价 |
| `data[].bidPx5` | 实数 | 是 | 买五价 |
| `data[].bidVol1` | 整数 | 是 | 买一量 |
| `data[].bidVol2` | 整数 | 是 | 买二量 |
| `data[].bidVol3` | 整数 | 是 | 买三量 |
| `data[].bidVol4` | 整数 | 是 | 买四量 |
| `data[].bidVol5` | 整数 | 是 | 买五量 |
| `data[].askPx1` | 实数 | 是 | 卖一价 |
| `data[].askPx2` | 实数 | 是 | 卖二价 |
| `data[].askPx3` | 实数 | 是 | 卖三价 |
| `data[].askPx4` | 实数 | 是 | 卖四价 |
| `data[].askPx5` | 实数 | 是 | 卖五价 |
| `data[].askVol1` | 整数 | 是 | 卖一量 |
| `data[].askVol2` | 整数 | 是 | 卖二量 |
| `data[].askVol3` | 整数 | 是 | 卖三量 |
| `data[].askVol4` | 整数 | 是 | 卖四量 |
| `data[].askVol5` | 整数 | 是 | 卖五量 |
| `data[].bidVolTotal` | 整数 | 是 |  |
| `data[].askVolTotal` | 整数 | 是 |  |
| `data[].activeBuyVol` | 整数 | 是 | 外盘(主动买入总量) |
| `data[].activeSellVol` | 整数 | 是 | 内盘(主动卖出总量) |
| `data[].mktCap` | 字符串 | 是 | 总市值 |
| `data[].floatCap` | 字符串 | 是 | 流通市值 |
| `data[].totShr` | 字符串 | 是 | 总股本 |
| `data[].floatShr` | 字符串 | 是 | 流通股本 |
| `data[].ordImbRatio` | 字符串 | 是 | 委比 |
| `data[].pb` | 字符串 | 是 | 市净率 |
| `data[].volRatio` | 整数 | 是 |  |
| `data[].turnover` | 字符串 | 是 | 换手率 |
| `data[].pe_ttm` | 字符串 | 是 | TTM市盈率 |
| `data[].pe_static` | 字符串 | 是 | 静态市盈率 |
| `data[].amplitude` | 字符串 | 是 | 振幅 |
| `data[].highLimit` | 字符串 | 是 | 涨停价格 |
| `data[].lowLimit` | 字符串 | 是 | 跌停价格 |
| `data[].avgPrice` | 字符串 | 是 |  |
| `data[].chineseName` | 字符串 | 是 | 中文名称（美股）。 |
| `data[].pe_dyn` | 字符串 | 是 | 动态市盈率 |

**响应示例**:

```json
{
  "msg": "ok",
  "code": 200,
  "data": [
    {
      "code": "600519",
      "name": "贵州茅台",
      "type": "STOCK",
      "exchangeCode": "XSHG",
      "countryCode": "CHN",
      "timestamp": 1782350365000,
      "updateTime": 1782350365000,
      "localDate": "2026-06-25 09:19:25",
      "price": "1207.7",
      "open": "0",
      "high": "0",
      "low": "0",
      "preClose": "1207.68",
      "volume": "0",
      "amount": "0",
      "change": "0.02",
      "changeRate": "0",
      "bidPx1": "1207.7",
      "bidPx2": "0",
      "bidPx3": "0",
      "bidPx4": "0",
      "bidPx5": "0",
      "bidVol1": 16900,
      "bidVol2": 3100,
      "bidVol3": 0,
      "bidVol4": 0,
      "bidVol5": 0,
      "askPx1": "0",
      "askPx2": "0",
      "askPx3": "0",
      "askPx4": "0",
      "askPx5": "1207.7",
      "askVol1": 0,
      "askVol2": 0,
      "askVol3": 0,
      "askVol4": 0,
      "askVol5": 16900,
      "bidVolTotal": 20000,
      "askVolTotal": 16900,
      "activeBuyVol": 0,
      "activeSellVol": 0,
      "mktCap": "1509723549527",
      "floatCap": "1509723549527",
      "totShr": "1250081601",
      "floatShr": "1250081601",
      "ordImbRatio": 8.4,
      "pb": 5.636,
      "volRatio": 0,
      "turnover": 0,
      "pe_ttm": 18.252,
      "pe_static": 18.34,
      "amplitude": 0,
      "highLimit": "1328.45",
      "lowLimit": "1086.91",
      "avgPrice": "0"
    },
    {
      "code": "000001",
      "name": "平安银行",
      "type": "STOCK",
      "exchangeCode": "XSHE",
      "countryCode": "CHN",
      "timestamp": 1782350352000,
      "localDate": "2026-06-25 09:19:12",
      "price": "10.49",
      "open": "0",
      "high": "0",
      "low": "0",
      "preClose": "10.51",
      "volume": "0",
      "amount": "0",
      "change": "-0.02",
      "changeRate": "-0.19",
      "bidPx1": "10.49",
      "bidPx2": "0",
      "bidPx3": "0",
      "bidPx4": "0",
      "bidPx5": "0",
      "bidVol1": 314400,
      "bidVol2": 0,
      "bidVol3": 0,
      "bidVol4": 0,
      "bidVol5": 0,
      "askPx1": "10.49",
      "askPx2": "0",
      "askPx3": "0",
      "askPx4": "0",
      "askPx5": "0",
      "askVol1": 314400,
      "askVol2": 30300,
      "askVol3": 0,
      "askVol4": 0,
      "askVol5": 0,
      "mktCap": "203568000000",
      "floatCap": "203565000000",
      "totShr": "19405918198",
      "floatShr": "19405600653",
      "ordImbRatio": 4.6,
      "pb": 0.45,
      "volRatio": 0,
      "turnover": 0,
      "pe_ttm": 4.73,
      "pe_dyn": 3.5,
      "pe_static": 4.77,
      "amplitude": 0,
      "highLimit": "11.56",
      "lowLimit": "9.46"
    }
  ]
}
```

---

### <a id="api-67"></a>67. GET 实时行情(返回整个市场实时行情)

| 属性 | 值 |
|------|----|
| **路径** | `/api/stock/v2/realtimeMarket` |
| **方法** | `GET` |
| **适用版本** | 企业版 |

**请求参数**:

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| `token` | query | string | 否 | token,通过登录获取 |
| `countryCode` | query | string (CHN, HKG, USA) | 否 | 国家/地区代码，和交易所，股票市场三选一。（CHN：中国大陆，HKG：中国香港，USA：美国）） |
| `exchangeCode` | query | string (XSHG, XSHE, BJSE, XHKG, XNAS, XNYS, AMEX) | 否 | 交易所代码，和国家/地区，股票市场三选一。（XSHG：上交所，XSHE：深交所，BJSE：北交所，XHKG：香港交易所，XNAS：纳斯达克，XNYS：纽约证卷交易所，AMEX：美国证卷交易所） |
| `market` | query | string (cn_hs, cn_hs_a, cn_hs_m, cn_hsj, cn_cyb, cn_kcb, cn_bjs, hk_main, hk_cyb, hk_gq, hk_hc, us_tech, us_china, us_star) | 否 | 股票市场，和国家/地区，交易所三选一。
（cn_hs：沪深所有，cn_hs_a：沪深A股，cn_hs_m：沪深主板，cn_hsj：沪深京所有，cn_cyb：创业板，cn_kcb：科创板，cn_bjs：北交所，us_tech：美股科技股，us_china：美股中概股，us_star：美股明星股,hk_main：港股主板，hk_cyb：港股创业板，hk_gq：港股国企股，hk_hc：港股红筹股）。 |
| `fields` | query | string | 否 | 返回的字段，中间以逗号分隔，字段名称点击”响应Response“可查看，输入all默认返回所有数据。 |
| `format` | query | string (json, csv) | 否 | 格式,支持json格式和csv格式（默认json格式） |

**成功响应 (200)**:

| 字段名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `msg` | 字符串 | 是 | 响应消息 |
| `code` | 字符串 | 是 | 代码 |
| `data` | 数组 | 是 | 响应数据 |
| `data[].code` | 字符串 | 是 | 代码 |
| `data[].exchangeCode` | 字符串 | 是 | 交易所代码。详见交易所清单接口。 |
| `data[].high` | 字符串 | 是 | 最高价 |
| `data[].low` | 字符串 | 是 | 最低价 |
| `data[].name` | 字符串 | 是 | 名称 |
| `data[].open` | 字符串 | 是 | 开盘价 |
| `data[].preClose` | 字符串 | 是 | 收盘价 |
| `data[].price` | 字符串 | 是 | 价格 |
| `data[].type` | 字符串 | 是 | 类型(STOCK：股票，INDEX：指数，FUND：基金，FOREX：外汇，CRYPTO：加密货币) |
| `data[].countryCode` | 字符串 | 是 | 国家/地区代码。详见国家/地区清单接口。 |
| `data[].chineseName` | 字符串 | 是 | 中文名称（美股）。 |
| `data[].localDate` | 字符串 | 是 | 更新时间。 |
| `data[].volume` | 字符串 | 是 | 成交量 |
| `data[].amount` | 字符串 | 是 | 成交额 |
| `data[].change` | 字符串 | 是 | 涨跌额 |
| `data[].changeRate` | 字符串 | 是 | 涨跌幅 |
| `data[].activeSellVol` | 整数 | 是 | 内盘(主动卖出总量) |
| `data[].activeBuyVol` | 整数 | 是 | 外盘(主动买入总量) |
| `data[].floatCap` | 字符串 | 是 | 流通市值 |
| `data[].mktCap` | 字符串 | 是 | 总市值 |
| `data[].floatShr` | 字符串 | 是 | 流通股本 |
| `data[].totShr` | 字符串 | 是 | 总股本 |
| `data[].ordImbRatio` | 字符串 | 是 | 委比 |
| `data[].pb` | 字符串 | 是 | 市净率 |
| `data[].turnover` | 字符串 | 是 | 换手率 |
| `data[].pe_ttm` | 字符串 | 是 | TTM市盈率 |
| `data[].pe_dyn` | 字符串 | 是 | 动态市盈率 |
| `data[].pe_static` | 字符串 | 是 | 静态市盈率 |
| `data[].amplitude` | 字符串 | 是 | 振幅 |
| `data[].highLimit` | 字符串 | 是 | 涨停价格 |
| `data[].lowLimit` | 字符串 | 是 | 跌停价格 |
| `data[].askPx1` | 实数 | 是 | 卖一价 |
| `data[].askVol1` | 整数 | 是 | 卖一量 |
| `data[].askPx2` | 实数 | 是 | 卖二价 |
| `data[].askVol2` | 整数 | 是 | 卖二量 |
| `data[].askPx3` | 实数 | 是 | 卖三价 |
| `data[].askVol3` | 整数 | 是 | 卖三量 |
| `data[].askPx4` | 实数 | 是 | 卖四价 |
| `data[].askVol4` | 整数 | 是 | 卖四量 |
| `data[].askPx5` | 实数 | 是 | 卖五价 |
| `data[].askVol5` | 整数 | 是 | 卖五量 |
| `data[].bidPx1` | 实数 | 是 | 买一价 |
| `data[].bidVol1` | 整数 | 是 | 买一量 |
| `data[].bidPx2` | 实数 | 是 | 买二价 |
| `data[].bidVol2` | 整数 | 是 | 买二量 |
| `data[].bidPx3` | 实数 | 是 | 买三价 |
| `data[].bidVol3` | 整数 | 是 | 买三量 |
| `data[].bidPx4` | 实数 | 是 | 买四价 |
| `data[].bidVol4` | 整数 | 是 | 买四量 |
| `data[].bidPx5` | 实数 | 是 | 买五价 |
| `data[].bidVol5` | 整数 | 是 | 买五量 |

**响应示例**:

```json
{
  "msg": "ok",
  "code": 200,
  "data": [
    {
      "code": "601136",
      "exchangeCode": "XSHG",
      "high": "0",
      "low": "0",
      "name": "首创证券",
      "open": "0",
      "preClose": "14.27",
      "price": "14.16"
    },
    {
      "code": "000878",
      "exchangeCode": "XSHE",
      "high": "0",
      "low": "0",
      "name": "云南铜业",
      "open": "0",
      "preClose": "17.45",
      "price": "17"
    }
  ]
}
```

---

### <a id="api-68"></a>68. GET 国家/地区

| 属性 | 值 |
|------|----|
| **路径** | `/api/ticker/v1/country` |
| **方法** | `GET` |

**请求参数**:

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| `token` | query | string | 否 | token,通过登录获取 |

**成功响应 (200)**:

| 字段名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `countryCode` | 字符串 | 是 | 国家代码 |
| `countryName` | 字符串 | 是 | 国家名称 |

---

### <a id="api-69"></a>69. GET 币种

| 属性 | 值 |
|------|----|
| **路径** | `/api/ticker/v1/currencyType` |
| **方法** | `GET` |

**请求参数**:

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| `token` | query | string | 否 | token,通过登录获取 |

**成功响应 (200)**:

| 字段名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `msg` | 字符串 | 是 | 响应消息 |
| `code` | 整数 | 是 | 响应状态码，200 表示成功 |
| `data` | 数组 | 是 | 响应数据 |
| `data[].CurrencyCode` | 字符串 | 是 |  |
| `data[].CurrencyName` | 字符串 | 是 |  |
| `data[].(数组元素)` | 字符串 | 是 | 标的类型(STOCK/INDEX/FUND/FOREX/CRYPTO/SECTOR/BOND/FUTURE) |

**响应示例**:

```json
{
  "msg": "ok",
  "code": 200,
  "data": [
    {
      "CurrencyCode": "AFN",
      "CurrencyName": "阿富汗尼"
    },
    {
      "CurrencyCode": "JMD",
      "CurrencyName": "牙买加元"
    }
  ]
}
```

---

### <a id="api-70"></a>70. GET 关键字搜索

| 属性 | 值 |
|------|----|
| **路径** | `/api/ticker/v1/search` |
| **方法** | `GET` |

**请求参数**:

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| `token` | query | string | 否 | token,通过登录获取 |
| `keyword` | query | string | 否 | 搜索关键字最少两个字符，如：医药 |
| `mode` | query | string | 否 | 模式默认全选，多种类型用逗号隔开，如：mode=name,pingying 表示只搜索名称和拼音。（all：所有，code：代码，name：名称，pingying：拼音） |
| `type` | query | string | 否 | 搜索类型默认全选，多种类型用逗号隔开，如：type=STOCK,FUND 表示只搜索股票和基金。（STOCK：股票，INDEX：指数，FUND：基金，FOREX：外汇，CRYPTO：加密货币，METAL：贵金属） |
| `countryCode` | query | string | 否 | 国家/地区代码默认全选，多种类型用逗号隔开。如：countryCode=CHN,HKG 表示只搜索A股和港股。 |
| `exchangeCode` | query | string | 否 | 交易所代码默认全选，多种类型用逗号隔开，如：exchangeCode=XSHG,XNAS 表示只搜索上交所和纳斯达克。 |
| `market` | query | string | 否 | 股票市场默认全选，多种类型用逗号隔开。（cn_hs：沪深所有，cn_hs_a：沪深A股，cn_hs_m：沪深主板，cn_hsj：沪深京所有，cn_cyb：创业板，cn_kcb：科创板，cn_bjs：北交所，us_tech：美股科技股，us_china：美股中概股，us_star：美股明星股,hk_main：港股主板，hk_cyb：港股创业板，hk_gq：港股国企股，hk_hc：港股红筹股）。 |
| `page` | query | string | 否 | 页码，一页100个，默认第一页。 |

**成功响应 (200)**:

| 字段名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `msg` | 字符串 | 是 | 响应消息 |
| `code` | 字符串 | 是 | 标的代码 |
| `data` | 对象 | 是 | 响应数据 |
| `data.page` | 整数 | 是 | 当前页码 |
| `data.pageTotal` | 整数 | 是 | 总页数 |
| `data.countTotal` | 整数 | 是 | 总条数 |
| `data.tickers` | 数组 | 是 | 标的列表 |
| `data.tickers[].code` | 字符串 | 是 | 标的代码 |
| `data.tickers[].name` | 字符串 | 是 | 名称 |
| `data.tickers[].type` | 字符串 | 是 | 类型(STOCK/INDEX/FUND/FOREX/CRYPTO/SECTOR/BOND/FUTURE/METAL) |
| `data.tickers[].exchangeCode` | 字符串 | 是 | 交易所代码 |
| `data.tickers[].countryCode` | 字符串 | 是 | 国家/地区代码 |
| `data.chineseName` | 字符串 | 是 | 中文名称 |

**响应示例**:

```json
{
  "msg": "ok",
  "code": 200,
  "data": {
    "page": 1,
    "pageTotal": 2,
    "countTotal": 143,
    "tickers": [
      {
        "code": "02335",
        "name": "麦科医药-B",
        "type": "STOCK",
        "exchangeCode": "XHKG",
        "countryCode": "HKG"
      },
      {
        "code": "01276",
        "name": "恒瑞医药",
        "type": "STOCK",
        "exchangeCode": "XHKG",
        "countryCode": "HKG"
      }
    ]
  }
}
```

---

### <a id="api-71"></a>71. GET 交易日历

| 属性 | 值 |
|------|----|
| **路径** | `/api/ticker/v1/tradeCals` |
| **方法** | `GET` |

**请求参数**:

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| `token` | query | string | 否 | token,通过登录获取 |
| `exchangeCode` | query | string (XSHG, XSHE, BJSE, XHKG, XNAS, XNYS, AMEX, SHFE, INE, DCE, ZCE, CFFEX, GFE, CBOT, NYMEX, COMEX, NYBOT) | 是 | 交易所代码，和国家/地区，股票市场三选一。（XSHG：上交所，XSHE：深交所，BJSE：北交所，XHKG：香港交易所，XNAS：纳斯达克，XNYS：纽约证卷交易所，AMEX：美国证卷交易所） |

**成功响应 (200)**:

| 字段名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `msg` | 字符串 | 是 | 响应消息 |
| `code` | 整数 | 是 | 响应状态码，200 表示成功 |
| `data` | 数组 | 是 | 响应数据 |
| `data[].exchangeCode` | 字符串 | 是 | 交易所代码 |
| `data[].tradingType` | 字符串 | 是 | 交易日类型(交易日/非交易日) |
| `data[].tradingTime` | 整数 | 是 | 交易时间戳 |
| `data[].tradingDay` | 字符串 | 是 | 交易日期(yyyy-MM-dd) |
| `data[].lastTradingTime` | 整数 | 是 | 上次交易时间戳 |
| `data[].lastTradingDay` | 字符串 | 是 | 上次交易日期(yyyy-MM-dd) |

**响应示例**:

```json
{
  "msg": "ok",
  "code": 200,
  "data": [
    {
      "exchangeCode": "XSHG",
      "tradingType": "交易日",
      "tradingTime": 1748966400000,
      "tradingDay": "2025-06-04",
      "lastTradingTime": 1748880000000,
      "lastTradingDay": "2025-06-03"
    },
    {
      "exchangeCode": "XSHG",
      "tradingType": "非交易日",
      "tradingTime": 1749052800000,
      "tradingDay": "2025-06-05",
      "lastTradingTime": 1748966400000,
      "lastTradingDay": "2025-06-04"
    }
  ]
}
```

---

## ws

### <a id="api-72"></a>72. GET 订阅实时行情

| 属性 | 值 |
|------|----|
| **路径** | `/ws` |
| **方法** | `GET` |
| **描述** | 如需要高频L2行情数据或者香港或美国等新加坡等外部地区服务器，请加技术人员企业微信。 |
| **适用版本** | 企业版 |
| **协议** | websocket |

**请求参数**:

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| `token` | query | string | 否 | token,通过登录获取 |

**成功响应 (200)**:

| 字段名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `msg` | 字符串 | 是 | 响应消息 |
| `code` | 字符串 | 是 | 代码 |
| `data` | 数组 | 是 | 响应数据 |
| `data[].localDate` | 字符串 | 是 | 更新时间。 |
| `data[].open` | 字符串 | 是 | 开盘价 |
| `data[].price` | 字符串 | 是 | 价格 |
| `data[].high` | 字符串 | 是 | 最高价 |
| `data[].low` | 字符串 | 是 | 最低价 |
| `data[].volume` | 字符串 | 是 | 成交量 |
| `data[].amount` | 字符串 | 是 | 成交额 |
| `data[].preClose` | 字符串 | 是 | 收盘价 |
| `data[].type` | 字符串 | 是 | 类型(STOCK：股票，INDEX：指数，FUND：基金，FOREX：外汇，CRYPTO：加密货币) |
| `data[].name` | 字符串 | 是 | 名称 |
| `data[].countryCode` | 字符串 | 是 | 国家/地区代码。详见国家/地区清单接口。 |
| `data[].exchangeCode` | 字符串 | 是 | 交易所代码。详见交易所清单接口。 |
| `data[].chineseName` | 字符串 | 是 | 中文名称（美股）。 |
| `data[].change` | 字符串 | 是 | 涨跌额 |
| `data[].changeRate` | 字符串 | 是 | 涨跌幅 |
| `data[].activeSellVol` | 字符串 | 是 | 卖盘 |
| `data[].activeBuyVol` | 字符串 | 是 | 买盘 |
| `data[].floatCap` | 字符串 | 是 | 流通市值 |
| `data[].mktCap` | 字符串 | 是 | 总市值 |
| `data[].floatShr` | 字符串 | 是 | 流通股本 |
| `data[].totShr` | 字符串 | 是 | 总股本 |
| `data[].ordImbRatio` | 字符串 | 是 | 委比 |
| `data[].pb` | 字符串 | 是 | 市净率 |
| `data[].volRatio` | 字符串 | 是 | 量比 |
| `data[].eps` | 字符串 | 是 | 每股收益 |
| `data[].bps` | 字符串 | 是 | 每股净资产 |
| `data[].turnover` | 字符串 | 是 | 换手率 |
| `data[].pe_ttm` | 字符串 | 是 | TTM市盈率 |
| `data[].pe_dyn` | 字符串 | 是 | 动态市盈率 |
| `data[].pe_static` | 字符串 | 是 | 静态市盈率 |
| `data[].amplitude` | 字符串 | 是 | 振幅 |
| `data[].highLimit` | 字符串 | 是 | 涨停价格 |
| `data[].lowLimit` | 字符串 | 是 | 跌停价格 |
| `data[].avgPrice` | 字符串 | 是 | 股息 |
| `data[].dividend` | 字符串 | 是 | 股息率 |
| `data[].dividendYield` | 字符串 | 是 | 均价 |
| `data[].sells` | 数组 | 是 | 卖盘 |
| `data[].buys` | 数组 | 是 | 买盘 |

**响应示例**:

```json
{
  "msg": "ok",
  "code": 200,
  "data": [
    {
      "localDate": "2025-06-03 09:30",
      "open": 1.134,
      "price": 1.134,
      "high": 1.134,
      "low": 1.134,
      "volume": 987,
      "amount": 111926,
      "preClose": 1.105
    },
    {
      "localDate": "2025-06-03 09:31",
      "open": 1.134,
      "price": 1.135,
      "high": 1.135,
      "low": 1.134,
      "volume": 8319,
      "amount": 943667,
      "preClose": 1.134
    },
    {
      "localDate": "2025-06-03 09:32",
      "open": 1.135,
      "price": 1.134,
      "high": 1.134,
      "low": 1.133,
      "volume": 2666,
      "amount": 302323,
      "preClose": 1.135
    },
    {
      "localDate": "2025-06-03 09:33",
      "open": 1.134,
      "price": 1.133,
      "high": 1.134,
      "low": 1.132,
      "volume": 705,
      "amount": 79911,
      "preClose": 1.134
    },
    {
      "localDate": "2025-06-03 09:34",
      "open": 1.133,
      "price": 1.133,
      "high": 1.134,
      "low": 1.133,
      "volume": 448,
      "amount": 50791,
      "preClose": 1.133
    },
    {
      "localDate": "2025-06-03 09:35",
      "open": 1.133,
      "price": 1.133,
      "high": 1.134,
      "low": 1.133,
      "volume": 1421,
      "amount": 160999,
      "preClose": 1.133
    },
    {
      "localDate": "2025-06-03 09:36",
      "open": 1.133,
      "price": 1.135,
      "high": 1.135,
      "low": 1.133,
      "volume": 2474,
      "amount": 280545,
      "preClose": 1.133
    },
    {
      "localDate": "2025-06-03 09:37",
      "open": 1.135,
      "price": 1.135,
      "high": 1.136,
      "low": 1.135,
      "volume": 352,
      "amount": 39954,
      "preClose": 1.135
    },
    {
      "localDate": "2025-06-03 09:38",
      "open": 1.135,
      "price": 1.134,
      "high": 1.135,
      "low": 1.133,
      "volume": 32,
      "amount": 3629,
      "preClose": 1.135
    },
    {
      "localDate": "2025-06-03 09:39",
      "open": 1.134,
      "price": 1.135,
      "high": 1.135,
      "low": 1.134,
      "volume": 710,
      "amount": 80544,
      "preClose": 1.134
    },
    {
      "localDate": "2025-06-03 09:40",
      "open": 1.135,
      "price": 1.133,
      "high": 1.135,
      "low": 1.133,
      "volume": 4824,
      "amount": 546612,
      "preClose": 1.135
    }
  ]
}
```

---
