OCTOPUS

Little Tornado website word count app


Where/how do you store the key(s) used for encryption?

Standard approach if you are using built in encryption on something 
like SQL or Oracle database, the database will generate an encryption 
key and encrypt this with another key protection key or Master key. 

This can be a pass-phrase or a longer key stored in e.g. .pem file.
This is usually stored in a restricted directory that only root/Administrator and the database service account can access. On database initiation the key is read and loaded into memory. This is then used to decrypt the encryption keys.
Firstly, in a system where the web and database servers are the same, how do you manage the key?

Key is stored in a directory on the server. To renew or revoke is usually through the database program.


