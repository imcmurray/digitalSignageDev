import redis, time, traceback, json
import digSig


def performUpdate(conf_id,ds_id):
    print('Got to performUpdate')
    digSig.processUpdate(conf_id,ds_id)
    time.sleep(10)


def redisCheck():
    try:
        r = redis.StrictRedis(host=config['REDIS']['hostName'],
                port=config['REDIS']['portNum'],
                password=config['REDIS']['authPass'])

        p = r.pubsub()
        p.subscribe('updates')

        while True:
            print('Waiting for the update command [%s]'%config['DIGSIG']['endpointId'])
            message = p.get_message()
            if message:
                if message['channel'] == 'updates':
                    if message['data'] == config['DIGSIG']['endpointId']:
                        performUpdate(config['DIGSIG']['configurationFileId'], config['DIGSIG']['endpointId'])

            time.sleep(0.5)

    except Exception as e:
        print('!!! Exception !!!')
        print(str(e))
        print(traceback.format_exc())

if __name__ == "__main__":
    # Load configuration from config.json
    with open('./digsig_config.json') as f:
        config = json.load(f)

    if 'DIGSIG' not in config:
        print('Sorry, did not find endpoint definition - contact support!')
        exit()
    else:
        redisCheck()
