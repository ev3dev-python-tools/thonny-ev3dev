def getContextualEv3API():
    import os

    return os
    if os.uname()[1] == 'ev3dev':
        import ev3cmd.ev3 as ev3
    else:
        #print(os.environ.get('EV3MODE'))
        myip=os.environ.get('EV3IP')
        if os.environ.get('EV3MODE') == "remote":
            import rpyc
            importEv3.conn = rpyc.classic.connect(myip) # host name or IP address of the EV3
            # note: attach connection to function importEv3 so that doesn't get garbage collected
            ev3 = importEv3.conn.modules['ev3dev.ev3']      # import ev3dev.ev3 remotely
            return ev3
        else:
            raise Exception("ev3 simulation not yet implemented")
    return ev3




