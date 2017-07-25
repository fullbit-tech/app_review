import boto.ec2
from flask import current_app


class AWS(object):

    def __init__(self):
        self.aws_access_key_id = current_app.config['AWS_ACCESS_KEY_ID']
        self.aws_secret_access_key = current_app.config['AWS_SECRET_ACCESS_KEY']

    @property
    def _security_groups(self):
        """Security groups to request"""
        raise NotImplementedError( "You must define security groups.")

    @property
    def _key_name(self):
        """Key pair name to request"""
        raise NotImplementedError( "You must define a key name.")


class EC2(AWS):
    """Creates an ec2 image object"""

    def __init__(self, ami_id, instance_type):
        super(EC2, self).__init__()

        self.connection = boto.ec2.connect_to_region(
            self._choose_region(),
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
        )
        self.ami_id = ami_id
        self.instance_type = instance_type

    @property
    def _instance(self):
        """Returns an instance object, if a reservation exists"""
        if self.reservation:
            return self.reservation.instances[0]

    @property
    def _permitted_groups(self):
        """Returns a list of permitted groups,
           if a reservation exists.
        """
        if self.reservation:
            return self.reservation.groups

    @property
    def _owner_id(self):
        """Returns an owner id, if a reservation exists"""
        if self.reservation:
            return self.reservation.owner_id

    @property
    def _security_groups(self):
        return ['app-review-ubuntu-1']

    @property
    def _key_name(self):
        return "app-review"

    def _choose_region(self):
        """Returns AWS region to use"""
        return 'us-east-2'

    def _run_instance(self):
        """Starts the instance"""
        self.reservation = self.connection.run_instances(
            self.ami_id,
            instance_type=self.instance_type,
            security_groups=self._security_groups,
            key_name=self._key_name)

    def _stop_instance(self):
        """Stops the instance"""
        if self._instance:
            self.connection.stop_instances(self._instance.id)

    def _terminate_instance(self):
        """Terminates the instance"""
        if self._instance:
            self.connection.terminate_instances(self._instance.id)

    def _get_instance_status(self):
        """Returns the instances status"""
        if self._instance:
            return self._instance.update()

    def start(self):
        self._run_instance()

    def stop(self):
        self._stop_instance()

    def terminate(self):
        self._terminate_instance()

    def status(self):
        return self._get_instance_status()
