def getEV3API():
    import os

    if os.uname()[1] == 'ev3dev':
        import ev3dev.ev3 as ev3
    else:
        #print(os.environ.get('EV3MODE'))
        if os.environ.get('EV3MODE') == "remote":
            myip=os.environ.get('EV3IP')
            import rpyc
            getEV3API.conn = rpyc.classic.connect(myip) # host name or IP address of the EV3
            # note: attach connection to function importEv3 so that doesn't get garbage collected
            ev3 = getEV3API.conn.modules['ev3dev.ev3']      # import ev3dev.ev3 remotely
            return ev3
        else:
            raise Exception("ev3 simulation not yet implemented")
    return ev3




