import socket

class sockConn:
    def __init__(self, robotIP, port):
        self.robotIP = robotIP
        self.port = port

    def send_command(self, command: str):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.robotIP, self.port))
        s.send(command.encode())
        s.close()
        print("Script Command Complete!")

    def build_command(self, moves: list) -> str:
        cmd = ''
        for line in moves:
            cmd += line + '\n'
        return cmd

moves = [
    'def moves():',
    'movel(pose_add(get_actual_tcp_pose(),p[0.10,0,0.05,0,0,0]))',
    'movel(pose_add(get_actual_tcp_pose(),p[-0.10,0,-0.05,0,0,0]))',
    'end'
]

robot = sockConn("192.168.0.2", 30002)
cmd = robot.build_command(moves)
robot.send_command(cmd)
