"""Generating CloudFormation template."""

from ipaddress import ip_network
from ipgetter2 import IPGetter
from troposphere import (
    Base64,
    ec2,
    GetAtt,
    Join,
    Output,
    Parameter,
    Ref,
    Template,
)

getter = IPGetter()

ApplicationPort = "3000"
PublicCidrIp = str(ip_network(getter.get().v4))

t = Template()

t.set_description("Effective DevOps in AWS: HelloWorld web application")

t.add_parameter(Parameter(
    "KeyPair",
    Description="Name of an existing EC2 KeyPair to SSH",
    Type="AWS::EC2::KeyPair::KeyName",
    ConstraintDescription="must be the name of an existing EC2 KeyPair.",
))

t.add_resource(ec2.SecurityGroup(
    "SecurityGroup",
    GroupDescription="Allow SSH and TCP/{} access".format(ApplicationPort),
    SecurityGroupIngress=[
        ec2.SecurityGroupRule(
            IpProtocol="tcp",
            FromPort="22",
            ToPort="22",
            CidrIp=PublicCidrIp,
        ),
        ec2.SecurityGroupRule(
            IpProtocol="tcp",
            FromPort=ApplicationPort,
            ToPort=ApplicationPort,
            CidrIp="0.0.0.0/0",
        ),
    ]
))

ud = Base64(Join('\n', [
    "#!/bin/bash",
    "sudo amazon-linux-extras install epel -y",
    "sudo yum install --enablerepo=epel -y nodejs",
    "sudo wget https://raw.githubusercontent.com/GarbhSoft/garbh-samples/master/devops/helloworld.js -O /home/ec2-user/helloworld.js",
    "sudo wget https://raw.githubusercontent.com/GarbhSoft/garbh-samples/master/devops/helloworld.service -O /lib/systemd/system/helloworld.service",
    "sudo systemctl daemon-reload",
    "sudo systemctl start helloworld"
]))

t.add_resource(ec2.Instance(
    "instance",
    ImageId="ami-0fc970315c2d38f01",
    InstanceType="t2.micro",
    SecurityGroups=[Ref("SecurityGroup")],
    KeyName=Ref("KeyPair"),
    UserData=ud,
)) 

t.add_output(Output(
    "InstancePublicIp",
    Description="Public IP of our instance.",
    Value=GetAtt("instance", "PublicIp"),
))

t.add_output(Output(
    "WebUrl",
    Description="Application endpoint",
    Value=Join("", [
        "http://", GetAtt("instance", "PublicDnsName"),
        ":", ApplicationPort
    ]),
))

print(t.to_json())
