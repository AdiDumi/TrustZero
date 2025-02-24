from flask import Flask, request, jsonify
import base64
import json
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import load_pem_private_key

app = Flask(__name__)

own_id = 5

servers = [1, 2, 3, 4, 5]

private_keys = {
"1":"-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQCWCNEsYivYW8/uLNkdqy72n0KJTEXPLTqZoLRtmFTlXMY4SVXsp1BAW9IYc/5AgjR1+b4ldqNl1WdeiO4Zqf0m4gN+1vwwD4cqhVgsFI8tbbmSo9NuQleHhloV7D1Q1nmpvcHX7A058Wg4u+pUeyBTyGZbpwoarK5Be9MIadWXu+Z9u+mftNgz/dNtuS8jfod7hCn3DcxFRE6UNMIhuJ/ELrtI1ch1vygtqk4GsJprM2tG7xJiV4IUxLKUIWuR9EpL/tZ89fewOrxppwvQ5S4iLBe+NUDkAyXPZNli1QGCtVdkx1SVw80n+Oo5Mi21KDT7EJA1HmRbgXNNpqPEmCOHAgMBAAECggEAPI7VgxEi+mLglBWVEwUX4SKaNBnNqZhraTv057GPPr7KIUj0fh9wZHHLZORYsQf9DctepPd0b3OKFB234TL8Q7gBSi6TPwDdgVuuIaiwu9joiNhITF5JvyGK9gNTInBXThySA8m68vLOKuwqYqwJ+ddO/Vp4WRjvAu5sWR6CwInQcyHWrcsHFVmrI65dXESaG5MuJNX7KQaDOvq+4HsUCCNPEJej40BGzrGlOGkx8bjLqAfxDLu42RTq/ariOTD81qwCcS/J7hshWh1YIfo+MkFPMWxd91tFFCa7iUt5/aXRttDMET9I1pdPNw34+s+PJdLot4FmlX5wHx7UBpEsJQKBgQDJgBx1ILSOOsX0xePQ2wDpFq3xFzOjoQIU6dTLPiw7VyzVwZCblSyppZKT8pf5+Yq2phE44akpPoMtKOaHXfEvRCvKe4+0O8gKJUW8yqcVkxTu43GPwDUKgUsdkoyAvZdrxxm45nvbda9EHDT61vqovKu8jhtf/v8mKejpRtOaNQKBgQC+nTNvI2FPMORJxmLRSEN9nR1lFkJW6ShW9wSQhUI/DGB62NKJuzDA5tfIOg7R2/drp7onDaxVUO7bsehdnUUVS4MKQHx/N0FUqC4DrOOroZ+Nl7J8bFKmB/t+aH6M4qLCFmcfH01X7aPGScQdQ7OjT8x3Ej6iwzVzC/QqDWDeSwKBgCOwpVm5qUFn95gbVPaxU7/1XGnPij35Tr0VjbNSF9OK5U4XMt3b1kVWJlg+J90G7iLb10ET9zpu8B0XmX1wjj+o+3ip2hI6ZHwnjeqamm2f151Ye8zSZpKtw/hA9NH4wtE8OrodWOLOPXT66gdj/JHWmTSUlxSxvc+srKxk9yXhAoGALN0RGwpnv9zRDnAsF/f7MpiFL6KykIQmI3nWUDGdKvu9xYw82X/+dJiglxbbIBe2v1bl4IU+V4JKBdl0yHvYo693MzWEV+joboV69xB9MYtD426d6t0QAtYEIndzubMp/aaKNPAIIzbigiwghYbGxBxnEmtv5J0velmI6VDmyMsCgYAl5rzBMX4S8PztSd0quZ8X+KYbw5pkiQCoiJAHjO97Z+Jm8D5UK3l5S2d8mnNHHYa4DG+RxyMrvXf5JY/q96SV4fh2v69+9fLVrtRQSnQwgQ5LYxq6dCFX54hmqIXojl++1a4/49QF104Jqd33vuIa2kcLUbWzRb9t9mDZVVJvAQ==\n-----END PRIVATE KEY-----",
"2":"-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCvpNz66fPHJ5qZ5Ji0//h3mcD0yhoy/W30OAWc1Cl4MCZqDxpHSpllKvhS5zPfvUzH17kz2mN1mIz64UV/mqEDNsmmqu28l1h8d9CVVyS2q7HFfckxYRN+VoJklOGeLNIChn36VRONetnY6ytN0bItdnf2wY/YshBExNw6Nhr1PA5g4b1WxsghvOxLdk7EvOkdtOJdg5Dz8jvdU6Y7cROZjkGfQKegvdPmiJnP0pm2xWEzQ4hBOflv97Qkon9orOaIhx8lmpjl0G83ph2NjRfKIphjMwd4091rr5E/DkflpCjnCe4OrPA3VIKCAqY44dENLSwnOLRAZgSAFj7Fd2mVAgMBAAECggEAIoyANw6rt+HPZDP14axz2DqzHLNgQeVdqmsWl4mX+p8l/zinR5yh3ad9HvmBV6IppymEsXFknO371SFYhUgKIdK2CYWXq7/tVNZQff+dJh1Ro3IhkAfzSKeFkHlEg9N3H64Ku6HebbbbgPKJGw6DSLQD1tKuE8a6snwygXTBCrmIsECnsID9xYbWI2kuD/V0M4E6qtRZHIYQg5zEDvsHxYuaniTh3sQOuHLMYZbyJQPXjB4xZxrMp2VGw3VJtG0Z4FlweKpjXkmVmjdBB6kRT05HJjJuM5hnp2LSee19/ILY8RQx9Y/LtmAUYyG9L8I2vvf7z033dveJnKkyUI57IQKBgQDniMrjh2gUFy9EXtucOTmryWgSEg8rCSfkVGjldGat5DbI+rtDg/CCKokXOCGPNtzO6P1M5z9MJopisMuMnGJ2SZ4zHg5JJjGhig1NZAYyr6s9E7x2mmOeucCLFUVk0/JcLOWmEEGusLRl1Te2Gvap2UxZNmxqWpoquG8Bpp2HrQKBgQDCNDAIb3VMEe3CaTZIKJXsbOBwz/jltg/OrJ4aw0kYtE0zdaTySew1vkWEDeypluKphpc5wcHiru1D7xUacR9wKEjNzWJoo1ehsd6SgJYHJ2H1rvPjEGQlW/7BRygSbq1DTjnoHsswPszbz9dNvcYqft7Xrl/sdpY9gcYepGLGiQKBgQCq+i05UGjfTS+ugY4TE38vCJA9p/Bji2NWDa9Yolig2QJL8DwRY4Fb3iVWbDD8HTt54DwNakcn6N4QexYVQ/bB+yNEBFHwWrAT5mpkWBTroSYG+GgX/XLLZ8hz7MVN6+Xxg4Yi16ZpZjwRZx6477hvPPRQfQwajcWC/qeaxHtYEQKBgDTJprzEPyf8P5p2qtCWZ5oqRh+kCE24XTeaaCdyKa5TZCC2u604NsKtA4xPlKLMZrQZ54VFi4QodEng9OWJFjiQWqnGSBeVPr6u8Ib1+NHc/J2hfp2b2PzmsqqqwtOvzdzbqJXVuPlWOK0PI8D38qOedMg/l8dYvKHfYpD1sfuxAoGBAL32NIZfbvR7Okh2ytbg74OXhfX1zZYNS1+14RjMQVo73QZ36vS79Sr9FcN3qBHBDveq6ufgpGq/w0YhbygWkzTsX3GBdmG5tSnnB267PFizfzETlKUTEIkgHeRPftsyijMoq3MfurZA6hIy9DDV53WL+AlD71Nqhh72vLHsbXGy\n-----END PRIVATE KEY-----",
"3":"-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQD6d7+g3PtBL3jwsCXoxssQHau7Ma+YcwAZzA4x8GmEK275V3tNCX0BLz7GS4TdEi9GI89wahHXefS/iUz3jQV7nr2wAEorjAWXu814bngHabGgXyKWSyzMzLW011UB9xvGe2amvOX3BA2PNowiEd0WDkzfJmfnh/+MiAfit20dDFY2sQj4UKDsmWVnccKjDq8F1N2S2T5KBe3c1rwZpFyDwT0Gl6nvjMaoMNjvtDS45o9yNBhgZYJhRwuxPXLzBePkmFCH5dVR0xResBuiY7G1IsHnTAsL76YEBLoc9vVhZ26pBO7p9RVmwp8BivoYFFIT/NNYgC+imc0iSZ6+m1nxAgMBAAECggEADawixEu71XObdPwQnbPYWuFbwgS00qwYadAXSEeY4vOiA69wViS586oaEaYGszCubvQ+eyL3JV2NbDU5A9xpW7WvIh/p7JWgqodAcJ4LJFBzN09qKm0hHW7hTmVgyRItrHiJAnoWTZUljldKcAOsn2sZbCcDDgMBArFcSNZ9eNPbbYg/aiUJGTi6IvtuChsQDKTuglcaFFu7/4NlSO3FPteH9POzfW5gW0EXBGTydBgUCaTBIqZbRi1fvIsF5fqoazfWQY0oot7oJ20BnXiEwfsvLUI1zXugqcsIZutFe/CPIzGpZ4seGfeeuToQWMiMh5EDv+rEUbRk9g80fEfs1wKBgQD+2SmEhHiKkeAZGKmuN0sYxBocWyQPm40tzty4PN6sdZpN0miOOBYYJTrg23cbHNKd2IPk537CDbZg/zxPKBbRNGZTg94GcY7NZc6IlrazWbISOLeRKlFTJF0xr/gBanODVg1vENhykfrn4lPnj44SCE+RRdzXpwJu7DF5UMiyNwKBgQD7mYS6/NibSpmSdKq9QqV8TVLE/aFUpWWnhzQ+BCAW1z8+K3FNzEvw1jkJHG9F+RDSUD+erGyI+T90R/jhB1M56T6n8NvkxVJogl56AHehZyTlCGTQWISEOAPUR/O5qk+LT3mMtsMkWIDSt/i9Y8liosTisL67zwfq3NA6ExfhFwKBgQDqMiLnNt2XagroxTNZeFK4xa3BFTiEZ0xMJmfLn5R6I/DTR2LyHzSep8f9z3EbJ1ed2tUKTHq+Vd+eL6/6hjrBske+w9YLUdwLgV1VRDtNgkYUXK7E5oCpyScjfDSLCIpyzWe3A2IFl4VeBy1YBSJoC98i/3K9cyrXSJMGi2iD7QKBgG4G8NilAkTHFunJQ3GI173IQs4K7KaLvizJH7uPKklS0EFr1hzjnsIvrLmjSbYb+ZM/rNLDLKOp/Gnpn5kpDuhgbBodZsxgzm0Ntis8URSwep3+UbgbPbhklqga3ybup+KQWuOCeUxHt+5urcSFAuizrc5E5ORU4W2AKz96YhL5AoGAeOxAV7S2IDqQSBIXxOovEv4MkPj6wtf+gxoCcWtLuivynnTbemvgBmGbDddJh0FaMOnE2fiDPhIfyi9yD8b0svGXniABMSf3QUdFM9e08HPX1fmffpbFCpoYej8SffY+u7O2PsUkWHHXZMpgoFksBDUcs5Ht2sretmTSak7m2cU=\n-----END PRIVATE KEY-----",
"4":"-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCIN1EHLhTnVaT3VpHnEmc443tCZ4i49NQ/iQNNX7PSEWZ27BSWCCDzZAG1YTGS7Hdh7li0lMpQLZ3G/nTuXPqiOs59r+E1rzGlcjqqpOiKDpGqhSKwfpZf9Q9/hy8b7kBVIP7lx+csl/VEXx55O1eLEuocEQZSeYJaGbc4GwEwTBbUBswOKqc4bmIzf6rMkxUJB9zfpYCqHVWjfNFKlJSDBUwaf86dNRt1xq+W40emxgPLTCn97Eez+ZZqGApfGV/SjagzNCq/ViE6FSnyia8F89uxBEQgqt+RLETIOum5GAVUHvnw1g5RuwaCLxHHZlMBLuEqvVR1hR2CB3uWaK5dAgMBAAECggEAA7FQMvwhJCzjdDocLa08ArT/SemF1ywX65in0fAtUQbcQkOUhnY2IJTdbTovb2mGpL5BCYe1xHGLbIEiwZdYjrxrjZvwbAakiji7BNJ43NwQTo1aKU0bUmwzinFYhEOGj9GjFIGjTZpCvOabkefTt3NqIzocsAcmWlWVXZ41FgMkJe07q16cylGTDALxDim8yztw9vTgvuw1aHdDuprloJGbeoe+0IrBmtofjBrn5XpPzrXAa/QLBqjXtPYgjBh5gkfvFbAPA+QMW7/xVe9VumXoPXDmvVSdva9hJMmcjcicPMRx6Mnom/NulEJ2xCDL25m5eDSH9KnlOnO0XLF65wKBgQC+6vlP9Lhc3UQlrcwWWOjKa/OY47wyUkbznglnE8/LFAG66jjza/jrx/Sz6yTek1XfUGQDUCuhNv+Iv2WLU5ZzgZd5zUfHeRuO2hpqqXzcl8V4EzT82twodV+ucnGUah6Iya/wSjSz/PmKlLVWEgDYGGo+kMh2pCxr64iP1eawewKBgQC2pqAf7qb8EWDwgSjxfeeQJLFfKirCVn8NabclGfuMGM7DN0vwVkP5z3NF0RVnptmkTRSmEQNSfpstoPk/2mKJqfxwY21+AtSMBYEemZl48JreKAjqWXep5/AIm3Ymd7VUyuxnWbOq4gei+IBAfIeTzBth5GGIVnOTByydau4hBwKBgQCRqw9Wpk4U7O6WISla07Oq3vsaaIirjIN+VdKuxzsAo98+EoApmvRuUj6vGHclLB2VKe1lacIgW6pVWFPOHpToxLQixzJBTHJuaJNHVtJiLZsJpv4C/6qDZCsBG2j16JIrpFeNa9ESk66Cwjwp08q5FsfZvPZ3L4SFQ00LEhXWCQKBgFLGvwjZunnAUoOMtYaEPd6Ykn4DeS9rzdbBU0wQM20xjPrx44t/PP1I4///GslH15jbigEc8rl/QUpziqJCkae8DvjMRsH1/Gec0wCQMfqaaEVINYonk9C/mYv9EJWsaNSNxoesIn3ORBG6tz0CctsrhDlgLEeCjoxSkwigfl0fAoGBAKbsz4rx0aaAMpEmRZQUX9ERCfOHnFGkSP5X+Me66KoLvsZv2oQqq0zv2LLVC0a8erpk6hoiPG5Tn5PVnqLq27uIJVmI05LjbuzQH1qdlS5coz82QHIU3/qU+U8nmC/9whG8V2PssT6KiZIMozUaes314fibcRo/5BTvg+adbD7Q\n-----END PRIVATE KEY-----",
"5":"-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCUDHzE04kSQrm2drX6BRzKbglMtIU3AqYViN9kiPMyaoU5S0kAswGwBUWeWi1aglSGPoaj0OI/NIvkBXCsHbbMhYMBafs9/oO4dDaGVGHaXd8jxRQlikoSJWbN+QXhq0hscpELruWI41pT7yB0bWmwgaVJB0dkJzn78FGQQPgBTgp73DrEB0tN5M0oHd62ed/ZpE8obCbPcyK8a7n/+D28W+IKZLA/CtZVCshxXMknvj/d1Kz5T+Z8dcKQcpFH6B55039MxAo7yTTkCNAyjG9vK/84EV6ArtUUjF+AQbkgciABMM3hzJoJvB0jilBNOdkagVHENAFdc8s7gtyDCOIpAgMBAAECggEAHxN58yTF/m/EJMFJVHhTQUiUqiWwWsozC40l+yfmCJykZ1Deu4dXoNeSc/lQ0NFPpbglMeisPQEuJghgTLiWANs7kwXoh2xPwN2f/lVjDt+qcYsyPekHwERajnypl+OIub7YpF+rba7vbHPi152J1FN6Wthsy2CSgshAjqucg0VJIj9d3oorvSmkrmZEO2LgkcSKuw3/rFyp4L2bL77axzfvr3b+bdGUIFxqQGvg4OiXcBDTRQo0D/Iod0VUfjKfDcEaLYsmSIRHCU0AjkZ2mBKRBmwo9HWVnCShbJdsphOGzakCoBOJa7zqEIqCtnrUoTAU8qx+iYKv4McbaNcRcwKBgQDCwRi+1fwN+U8n3q+QcybgMu0HOjv3y3RNfdWQdN8WwJ0hhDKYyzcbvMuLchKRxFyX9SDrqIGt/yWjHtNhkM4n1e3G1KRVuL9doPB/lxZJU1P5oIb3dToCLGq/UMAMFcniTk/mHs2E6M7rYShVsUTtjYMJyXKz13zFrHHM2ZFg6wKBgQDCm1BRWBHzzs3LBp/JHoptcaPQypWN1UBvl63mYCNBuUS2p10SbA64voQ2PFqruCz5wAkoG2ptCiULMrnUgpfJPrS2yqtCl2fAjEHOoli9OcFkGZRewIZhacdJA9xt7+vqkTCRGJ/eH5u8R3KezMvWfm/S5NDRskULK5TGYROkOwKBgA58pKWVb1FuySeTFgYtuqeUwjL2bv2Iwdb91EQRnYKow0d5+PWKsEe87Hsr+hujuquHDXLaLwNNZnRS17B7QAqQjEZtDOhffMSvMxSanYrIywdXnJKNwsnkmfAvRonfmQvffWwFwI3xb2rs6D4vmIv/Kc8xj/m2vs5JfJGbYYgPAoGAYcYk2Wm1Q1iQ/sNqPmLwy8H/uyQ9dZBCGo8LmSaOMDREOLznvxy5XMqjpJg4OfSD7Es2jocPto8VQ4YN5Z5jYoH1y60R1Jg7UXtmiMn6ab/90Swk5mI2YfUCYkXlVvrm/ehKjWvgznn1BeijxvNAKplF16CM5f56P/16dx1JAAcCgYEAhs4qhhxgDSricEQwgZnDW+1NAS7A/LPHwi2INaauxh3HsCi46G96ziXr4lPbIH3+9VFYhO3eE8NSZm18okjQPbZ5dNr0wUzw6REL5hGilg/CpjY9ADxVwPp2QLAeGdMI+dJHEyhfEiaNjHJwR2fIx8yPWLZ2JnpcnErVLaWeU4Y=\n-----END PRIVATE KEY-----"
}

public_keys = {
"1":"-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAlgjRLGIr2FvP7izZHasu9p9CiUxFzy06maC0bZhU5VzGOElV7KdQQFvSGHP+QII0dfm+JXajZdVnXojuGan9JuIDftb8MA+HKoVYLBSPLW25kqPTbkJXh4ZaFew9UNZ5qb3B1+wNOfFoOLvqVHsgU8hmW6cKGqyuQXvTCGnVl7vmfbvpn7TYM/3TbbkvI36He4Qp9w3MRUROlDTCIbifxC67SNXIdb8oLapOBrCaazNrRu8SYleCFMSylCFrkfRKS/7WfPX3sDq8aacL0OUuIiwXvjVA5AMlz2TZYtUBgrVXZMdUlcPNJ/jqOTIttSg0+xCQNR5kW4FzTaajxJgjhwIDAQAB\n-----END PUBLIC KEY-----",
"2":"-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAr6Tc+unzxyeameSYtP/4d5nA9MoaMv1t9DgFnNQpeDAmag8aR0qZZSr4Uucz371Mx9e5M9pjdZiM+uFFf5qhAzbJpqrtvJdYfHfQlVcktquxxX3JMWETflaCZJThnizSAoZ9+lUTjXrZ2OsrTdGyLXZ39sGP2LIQRMTcOjYa9TwOYOG9VsbIIbzsS3ZOxLzpHbTiXYOQ8/I73VOmO3ETmY5Bn0CnoL3T5oiZz9KZtsVhM0OIQTn5b/e0JKJ/aKzmiIcfJZqY5dBvN6YdjY0XyiKYYzMHeNPda6+RPw5H5aQo5wnuDqzwN1SCggKmOOHRDS0sJzi0QGYEgBY+xXdplQIDAQAB\n-----END PUBLIC KEY-----",
"3":"-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA+ne/oNz7QS948LAl6MbLEB2ruzGvmHMAGcwOMfBphCtu+Vd7TQl9AS8+xkuE3RIvRiPPcGoR13n0v4lM940Fe569sABKK4wFl7vNeG54B2mxoF8ilksszMy1tNdVAfcbxntmprzl9wQNjzaMIhHdFg5M3yZn54f/jIgH4rdtHQxWNrEI+FCg7JllZ3HCow6vBdTdktk+SgXt3Na8GaRcg8E9Bpep74zGqDDY77Q0uOaPcjQYYGWCYUcLsT1y8wXj5JhQh+XVUdMUXrAbomOxtSLB50wLC++mBAS6HPb1YWduqQTu6fUVZsKfAYr6GBRSE/zTWIAvopnNIkmevptZ8QIDAQAB\n-----END PUBLIC KEY-----",
"4":"-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAiDdRBy4U51Wk91aR5xJnOON7QmeIuPTUP4kDTV+z0hFmduwUlggg82QBtWExkux3Ye5YtJTKUC2dxv507lz6ojrOfa/hNa8xpXI6qqToig6RqoUisH6WX/UPf4cvG+5AVSD+5cfnLJf1RF8eeTtXixLqHBEGUnmCWhm3OBsBMEwW1AbMDiqnOG5iM3+qzJMVCQfc36WAqh1Vo3zRSpSUgwVMGn/OnTUbdcavluNHpsYDy0wp/exHs/mWahgKXxlf0o2oMzQqv1YhOhUp8omvBfPbsQREIKrfkSxEyDrpuRgFVB758NYOUbsGgi8Rx2ZTAS7hKr1UdYUdggd7lmiuXQIDAQAB\n-----END PUBLIC KEY-----",
"5":"-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAlAx8xNOJEkK5tna1+gUcym4JTLSFNwKmFYjfZIjzMmqFOUtJALMBsAVFnlotWoJUhj6Go9DiPzSL5AVwrB22zIWDAWn7Pf6DuHQ2hlRh2l3fI8UUJYpKEiVmzfkF4atIbHKRC67liONaU+8gdG1psIGlSQdHZCc5+/BRkED4AU4Ke9w6xAdLTeTNKB3etnnf2aRPKGwmz3MivGu5//g9vFviCmSwPwrWVQrIcVzJJ74/3dSs+U/mfHXCkHKRR+geedN/TMQKO8k05AjQMoxvbyv/OBFegK7VFIxfgEG5IHIgATDN4cyaCbwdI4pQTTnZGoFRxDQBXXPLO4LcgwjiKQIDAQAB\n-----END PUBLIC KEY-----"
}

def load_private_key_from_file():
    return private_keys[str(own_id)]


def generate_certificate(user_pk, private_key):
    private_key = load_pem_private_key(private_key.encode('utf-8'), password=None)

    signature = private_key.sign(
        base64.b64decode(user_pk.encode('utf-8')),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return signature


def add_token_to_response(token_list, user_pk):
    # Load server private key
    private_key = load_private_key_from_file()
    # Generate certificate with it on the user public key
    signature = generate_certificate(user_pk, private_key)

    # search if the user already had a certificate from server and update it
    id_found = False
    for i in range(0, len(token_list), 2):
        pair = token_list[i:i + 2]
        key = pair[0]
        if int(key) == own_id:
            id_found = True
            token_list[i + 1] = base64.b64encode(signature).decode('utf-8')
            break

    if not id_found:
        token_list.append(str(own_id))
        token_list.append(base64.b64encode(signature).decode('utf-8'))
    return token_list


@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    specific_header_value = request.headers.get('User-Key-Signatures')

    # Simulate a login check (for demo purposes)
    if username != 'admin' or password != 'password':
        return jsonify({"message": "Login failed"}), 403

    status_code = 200
    response_data = {"message": "Login successful"}
    response = jsonify(response_data)

    parts = specific_header_value.split(":")
    user_public_key = parts[0]

    # Modify the response body to add the token
    header = add_token_to_response(parts[1:], user_public_key)

    response.headers['User-Key-Signatures'] = user_public_key + ":" + ":".join(header)
    return response, status_code


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=88, threaded=True)
