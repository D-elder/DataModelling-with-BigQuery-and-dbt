# -*- coding: utf-8 -*- #
# Copyright 2021 Google LLC. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Run trigger command."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.cloudbuild import cloudbuild_util
from googlecloudsdk.api_lib.cloudbuild import trigger_config as trigger_utils
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.cloudbuild import resource_args
from googlecloudsdk.command_lib.util.concepts import concept_parsers
from googlecloudsdk.core import properties
from googlecloudsdk.core import resources


class Run(base.Command):
  """Run a build trigger."""

  detailed_help = {
      'DESCRIPTION':
          'Run a build trigger.',
      'EXAMPLES': ("""
        To run a build trigger, run:

          $ {command} MY-TRIGGER --branch=master
       """),
  }

  @staticmethod
  def Args(parser):
    concept_parsers.ConceptParser.ForResource(
        'TRIGGER',
        resource_args.GetTriggerResourceSpec(),
        'Build Trigger.',
        required=True).AddToParser(parser)

    revision_config = parser.add_mutually_exclusive_group()
    revision_config.add_argument('--branch', help='Branch to run.')
    revision_config.add_argument('--tag', help='Tag to run.')
    revision_config.add_argument('--sha', help='SHA to run.')
    trigger_utils.AddSubstitutions(parser)

  def Run(self, args):
    """Runs a build trigger.

    Args:
      args: an argparse namespace. All the arguments that were provided to this
        command invocation.

    Returns:
      Some value that we want to have printed later.
    """

    client = cloudbuild_util.GetClientInstance()
    messages = cloudbuild_util.GetMessagesModule()

    project = properties.VALUES.core.project.Get(required=True)
    regionprop = properties.VALUES.builds.region.Get()
    location = args.region or regionprop or cloudbuild_util.DEFAULT_REGION
    trigger = args.TRIGGER

    name = resources.REGISTRY.Parse(
        trigger,
        params={
            'projectsId': project,
            'locationsId': location,
            'triggersId': trigger,
        },
        collection='cloudbuild.projects.locations.triggers').RelativeName()

    request = messages.RunBuildTriggerRequest(triggerId=trigger)

    if args.branch:
      request.source = messages.RepoSource(branchName=args.branch)
    elif args.tag:
      request.source = messages.RepoSource(tagName=args.tag)
    elif args.sha:
      request.source = messages.RepoSource(commitSha=args.sha)

    if args.substitutions:
      if request.source is None:
        request.source = messages.RepoSource()
      request.source.substitutions = cloudbuild_util.EncodeTriggerSubstitutions(
          args.substitutions, messages.RepoSource.SubstitutionsValue)

    return client.projects_locations_triggers.Run(
        client.MESSAGES_MODULE.CloudbuildProjectsLocationsTriggersRunRequest(
            name=name,
            runBuildTriggerRequest=request,
        ))
