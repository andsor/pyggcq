# -*- coding: utf-8 -*-

'''

   Copyright 2015 The pyggcq Developers

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

'''

import logging

import ggcq
import ggcq.ggcq
import pytest
import simpy


def test_ggcq():
    arrival_time_generator = iter([])
    service_time_generator = iter([1.0])
    queue = ggcq.GGCQ(
        arrival_time_generator,
        service_time_generator,
        capacity=1,
    )
    queue.run()
    assert len(queue._observer.jobs) == 1
    assert queue._observer.jobs[0] == [0.0, 0.0, 1.0]


def test_ggcq_arrival_time_wrong_type(caplog):
    arrival_time_generator = iter(['a'])
    service_time_generator = iter([1.0])
    queue = ggcq.GGCQ(
        arrival_time_generator,
        service_time_generator,
        capacity=1,
    )
    with pytest.raises(ggcq.GGCQArrivalTimeTypeError):
        queue.run()


def test_ggcq_negative_arrival_time_throws(caplog):
    arrival_time_generator = iter([-1.0])
    service_time_generator = iter([1.0])
    queue = ggcq.GGCQ(
        arrival_time_generator,
        service_time_generator,
        capacity=1,
    )
    with pytest.raises(ggcq.GGCQNegativeArrivalTimeError):
        queue.run()


def test_ggcq_negative_service_time_throws(caplog):
    arrival_time_generator = iter([])
    service_time_generator = iter([-1.0])
    queue = ggcq.GGCQ(
        arrival_time_generator,
        service_time_generator,
        capacity=1,
    )
    with pytest.raises(ggcq.GGCQNegativeServiceTimeError):
        queue.run()


def test_ggcq_not_enough_service_times(caplog):
    caplog.setLevel(logging.DEBUG)
    arrival_time_generator = iter([])
    service_time_generator = iter([])
    queue = ggcq.GGCQ(
        arrival_time_generator,
        service_time_generator,
        capacity=1,
    )
    with pytest.raises(ggcq.GGCQServiceTimeStopIteration):
        queue.run()


def test_dd1q():
    arrival_time_generator = iter([1.0])
    service_time_generator = iter([2.0, 1.0])
    queue = ggcq.GGCQ(
        arrival_time_generator,
        service_time_generator,
        capacity=1,
    )
    queue.run()
    assert len(queue._observer.jobs) == 2
    assert queue._observer.jobs[0] == [0.0, 0.0, 2.0]
    assert queue._observer.jobs[1] == [1.0, 2.0, 3.0]


def test_dd2q():
    arrival_time_generator = iter([1.0, 0.5])
    service_time_generator = iter([3.0, 1.0, 1.0])
    queue = ggcq.GGCQ(
        arrival_time_generator,
        service_time_generator,
        capacity=2,
    )
    queue.run()
    assert len(queue._observer.jobs) == 3
    assert queue._observer.jobs[0] == [0.0, 0.0, 3.0]
    assert queue._observer.jobs[1] == [1.0, 1.0, 2.0]
    assert queue._observer.jobs[2] == [1.5, 2.0, 3.0]


@pytest.fixture
def env():
    return simpy.Environment()


@pytest.fixture
def observer():
    return ggcq.ggcq.RawDataObserver()


def test_queue_process_job(caplog, env, observer):
    caplog.setLevel(logging.DEBUG)
    observer.notify_arrival(time=0.0, job_id=0)
    service_time_generator = iter([1.0])
    queue = ggcq.ggcq.Queue(
        env=env,
        service_time_generator=service_time_generator,
        observer=observer,
    )
    env.process(queue.process(0))
    env.run()
    assert len(observer.jobs) == 1
    assert observer.jobs[0] == [0.0, 0.0, 1.0]


def test_queue_not_enough_service_times(caplog, env, observer):
    caplog.setLevel(logging.DEBUG)
    observer.notify_arrival(time=0.0, job_id=0)
    service_time_generator = iter([])
    queue = ggcq.ggcq.Queue(
        env=env,
        service_time_generator=service_time_generator,
        observer=observer,
    )
    env.process(queue.process(0))
    with pytest.raises(ggcq.GGCQServiceTimeStopIteration):
        env.run()


def test_queue_service_time_value_error(caplog, env, observer):
    caplog.setLevel(logging.DEBUG)
    observer.notify_arrival(time=0.0, job_id=0)
    service_time_generator = iter(['1'])
    queue = ggcq.ggcq.Queue(
        env=env,
        service_time_generator=service_time_generator,
        observer=observer,
    )
    env.process(queue.process(0))
    with pytest.raises(ggcq.GGCQServiceTimeTypeError):
        env.run()
