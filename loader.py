import asyncio
import json

import aiohttp


URL_DEVEL = "http://10.10.127.19:8086/graphql"
MAX_CLIENTS = 1


SUBQUERY = "{subquery_name} {{ {subquery_fields} }}"
FLAG = SUBQUERY.format(subquery_name='flag', subquery_fields='ksm shortName name alfa2 alfa3')
COUNTRY = SUBQUERY.format(subquery_name='country', subquery_fields='ksm shortName name alfa2 alfa3')
VESSEL_TYPE = SUBQUERY.format(subquery_name='vesselType', subquery_fields='vesselTypeEn vesselTypeRu')
FLEET = SUBQUERY.format(subquery_name='fleet', subquery_fields='fcUuid abbreviation name region')
KEUZ = SUBQUERY.format(subquery_name='keuzClassifier', subquery_fields='clsfObjId relationTypeId kodKeuz')
PROJECT = SUBQUERY.format(subquery_name='project', subquery_fields='fc_Uuid TKPrjtthCode TKPrjtthKodprj TKPrjtthName TKPrjtthVmfcl TKPrjtthIgcl TKPrjtthDl TKPrjtthSh TKPrjtthOs TKPrjtthVistd TKPrjtthVipln TKPrjtthVin TKPrjtthVip TKPrjtthGrp TKPrjtthSpn TKPrjtthSpp TKPrjtthDaln TKPrjtthDalp TKPrjtthGl TKPrjtthCh TKPrjtthAvt TKPrjtthVoor TKPrjtthRgav  TKPrjtthDes TKPrjtthPrim TKPrjtthBegda TKPrjtthEndda TKPrjtthPr')
MODEL3D = SUBQUERY.format(subquery_name='model3d', subquery_fields='urlImg urlModel urlWaterlineModel urlWaterlineImg swiftUrlModel swiftUrlWaterlineModel swiftUrlImg swiftUrlWaterlineImg fileModel fileWaterlineModel fileImg fileWaterlineImg')

QUERY_RAW = """
                query {{
                    {query} {{
                        {fields}
                        {subquery}
                    }}
                }}
            """

CIVIL_FIELDS = ['imo',
                'mmsi',
                'name',
                'formerNames',
                'operatingStatus',
                'grossTonnage',
                'deadweight',
                'length',
                'breadth',
                'length',
                'engineType',
                'engineModel',
                'enginePower',
                'yearOfBuild',
                'builder',
                'classificationSociety',
                'homePort',
                'owner',
                'manager',
                'vesselTypeId',
                'ksm',
                'captain',
                VESSEL_TYPE,
                FLAG]
MILITARY_FIELDS = ['fc_Uuid',
                   'TKKplvmfCode',
                   'TKKplvmfName',
                   'TKKplvmfNamec',
                   'TKKplvmfNom',
                   'TKKplvmfPpb',
                   'TKKplvmfDatvv',
                   'TKKplvmfSost',
                   'TKKplvmfBegda',
                   'TKKplvmfEndda',
                   'TKKplvmfPr',
                   'TKKplvmfFl',
                   'TKKpligKsm',
                   'TKKpligNameclat',
                   'TKKpligCodealt',
                   'TKKplvmfInd',
                   'TKPrjtthCode',
                   'TKPrjtthVmfcl',
                   'commonClassifierId',
                   'relationTypeId',
                   'nameShort',
                   'abbreviation',
                   'serviceTime',
                   'technicalReadinessName',
                   'technicalReadinessEvent',
                   'alertName',
                   'alertWhoseOrder',
                   'alertOrderNum',
                   'alertOrderDate',
                   FLEET,
                   COUNTRY,
                   PROJECT,
                   KEUZ,
                   MODEL3D]


def civil_query():
    civil_fields = (' '.join(CIVIL_FIELDS))
    civil_node = SUBQUERY.format(subquery_name='node', subquery_fields=civil_fields)
    civil_edge = SUBQUERY.format(subquery_name='edges', subquery_fields=civil_node)
    return {'query': QUERY_RAW.format(query=' civilVesselsData(onlyIdentified: false)',
                                      fields='', subquery=civil_edge)}


def military_query():
    military_fields = (' '.join(MILITARY_FIELDS))
    military_node = SUBQUERY.format(subquery_name='node', subquery_fields=military_fields)
    military_edge = SUBQUERY.format(subquery_name='edges', subquery_fields=military_node)
    return {'query': QUERY_RAW.format(query=' shipData(onlyIdentified: false)',
                                      fields='', subquery=military_edge)}


async def fetch_async(pid, type_):
    civil_string = civil_query()
    military_string = military_query()
    print('Fetch async process {} started'.format(pid))
    async with aiohttp.request('POST', URL_DEVEL, json=military_string if type_ == 'mil' else civil_string) as resp:
        response = await resp.text()
    return json.loads(response)


async def asynchronous(type_):
    results = []
    futures = [fetch_async(i, type_) for i in range(1, MAX_CLIENTS + 1)]
    done, pending = await asyncio.wait(futures)
    for i in range(1, MAX_CLIENTS + 1):
        results.append(done.pop())
    return results
