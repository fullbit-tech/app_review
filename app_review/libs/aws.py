import time
import boto.ec2
from flask import current_app


class AWS(object):
    """Base class for AWS calls"""

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
    """Creates an ec2 object for working with instances"""

    def __init__(self, instance_id=None, ami_id='ami-5c557539',
                 instance_type='t2.micro'):
        super(EC2, self).__init__()

        self.connection = boto.ec2.connect_to_region(
            self._choose_region(),
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
        )
        self.ami_id = ami_id
        self.instance_type = instance_type
        self._reservation = None
        if instance_id:
            reservations = self.connection.get_all_reservations(
                instance_id)
            if reservations:
                self._reservation = reservations[0]

    def start(self, user_data=None):
        if self.instance:
            self._start_instance()
        else:
            self._create_and_start_instance(user_data)

    def stop(self):
        self._stop_instance()

    def terminate(self):
        self._terminate_instance()

    @property
    def state(self):
        return self._get_instance_state()

    @property
    def instance(self):
        if self._reservation:
            return self._reservation.instances[0]

    @property
    def _permitted_groups(self):
        """Returns a list of permitted groups,
           if a reservation exists.
        """
        if self._reservation:
            return self._reservation.groups

    @property
    def _owner_id(self):
        """Returns an owner id, if a reservation exists"""
        if self._reservation:
            return self._reservation.owner_id

    @property
    def _security_groups(self):
        return ['app-review-ubuntu-1']

    @property
    def _key_name(self):
        return "app-review"

    def _choose_region(self):
        """Returns AWS region to use"""
        return 'us-east-2'

    def _wait_for_status(self, status):
        while self.instance.state != status:
            time.sleep(2)
            self.instance.update()

    def _create_and_start_instance(self, user_data):
        """Create and starts an instance"""
        self._reservation = self.connection.run_instances(
            self.ami_id,
            instance_type=self.instance_type,
            security_groups=self._security_groups,
            key_name=self._key_name, user_data=user_data)
        self._wait_for_status('running')

    def _start_instance(self):
        """Starts the instance"""
        if (self.instance and self.state != 'running' and
                              self.state != 'terminated'):
            self.instance.start()
            self._wait_for_status('running')

    def _stop_instance(self):
        """Stops the instance"""
        if self.instance:
            self.connection.stop_instances(self.instance.id)
            self._wait_for_status('stopped')

    def _terminate_instance(self):
        """Terminates the instance"""
        if self.instance:
            self.connection.terminate_instances(self.instance.id)
            self._wait_for_status('terminated')

    def _get_instance_state(self):
        """Returns the instance status"""
        if self.instance:
            return self.instance.update()

