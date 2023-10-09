# panic-response-validator
Validate panic response for PCDDS APIs
 - watch
 - V5 retry api
   
**Set-up required to run script**
- Install python3
- Install pip

**Download dependencies using pip**
* python3 -m pip install validators
* python3 -m pip install ftputil

**Execution**
```
usage: validate_panic_response.py [-h] -c CONTENT_ID -p PASSWORD

required arguments:
  -c CONTENT_ID, --content_id CONTENT_ID
                        content-id
  -p PASSWORD, --password PASSWORD
                        filezilla password
optional arguments:
  -h, --help            show this help message and exit
```
**Sample Command for execution**
```
python3 validate_panic.py -c <content-id> -p <filezilla-password>
```
**Validation**
- url validation
   1. contains apmf
   2. acl till apmf
   3. type=free
   4. ttl=86400
- tag_combination validation
   1. ads: non_ssai
   2. resolution: sd
   3. language: hin

**Response**

**Success**
```
----------- Content-id: 1540025574 -----------

----------- Validating Watch panic response -----------
----------- android -----------
airtel : '✓'
akamai : '✓'
cloudfront : '✓'
gme : '✓'
----------- androidtv -----------
airtel : '✓'
akamai : '✓'
cloudfront : '✓'
gme : '✓'
.
.
.
----------- Validating V5 panic response -----------
----------- android -----------
airtel : '✓'
akamai : '✓'
cloudfront : '✓'
gme : '✓'
----------- androidtv -----------
airtel : '✓'
akamai : '✓'
cloudfront : '✓'
gme : '✓'
.
.
.
```

**Failure**
```
----------- Content-id: 1540025598 -----------

----------- Validating Watch panic response -----------
----------- android -----------
airtel : '✕' - invalid tag_combination
akamai : '✕' - invalid tag_combination
cloudfront : '✕' - invalid tag_combination
gme : '✕' - invalid tag_combination
.
.
.
```
