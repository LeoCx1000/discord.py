from __future__ import annotations

from random import randint
from typing import Any, Dict, List, Mapping, Optional, Sequence, Union, TYPE_CHECKING

from . import abc
from .colour import Colour
from .enums import (
    ChannelType,
    ContentFilter,
    ForumOrderType,
    NotificationLevel,
    VerificationLevel,
    VideoQualityMode,
    ForumLayoutType,
)
from .flags import SystemChannelFlags
from .permissions import PermissionOverwrite, Permissions
from .utils import _bytes_to_base64_data
from .channel import ForumTag
from .partial_emoji import _EmojiTag, PartialEmoji
from .state import ConnectionState
from .guild import Guild

if TYPE_CHECKING:
    from .message import EmojiInputType

__all__ = ()


class NewRole:
    def __init__(
        self,
        *,
        name: Optional[str],
        permissions: Optional[Permissions] = None,
        colour: Optional[Union[Colour, int]] = None,
        hoist: Optional[bool] = None,
        mentionable: Optional[bool] = None,
    ):
        self.id = randint(0, 999_999_999_999)
        self.name = name
        self.permissions = permissions
        self.colour = colour
        self.hoist = hoist
        self.mentionable = mentionable

    @property
    def color(self):
        return self.colour

    def _to_payload(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {'id': self.id}
        if self.permissions is not None:
            payload['permissions'] = str(self.permissions.value)

        actual_colour = self.colour or Colour.default()
        if isinstance(actual_colour, int):
            payload['color'] = actual_colour
        else:
            payload['color'] = actual_colour.value

        if self.hoist is not None:
            payload['hoist'] = self.hoist

        if self.mentionable is not None:
            payload['mentionable'] = self.mentionable

        if self.name is not None:
            payload['name'] = self.name

        return payload


class NewGuildChannel:
    def __init__(
        self,
        *,
        name: str,
        type: ChannelType,
        category: Optional[NewCategory],
        overwrites: Optional[Dict[NewRole, PermissionOverwrite]],
        guild: NewGuild,
    ) -> None:
        self.id: int = randint(0, 999_999_999_999)
        self.name: str = name
        self.guild: NewGuild = guild
        self.type: ChannelType = type
        self.category: Optional[NewCategory] = category
        self.overwrites: Optional[Dict[NewRole, PermissionOverwrite]] = overwrites

    def _to_payload(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {'id': self.id, 'name': self.name, 'type': self.type.value}

        overwrites = self.overwrites
        if overwrites is None:
            overwrites = {}
        elif not isinstance(self.overwrites, Mapping):
            raise TypeError('overwrites parameter expects a dict.')

        perms = []
        for target, perm in overwrites.items():
            if not isinstance(perm, PermissionOverwrite):
                raise TypeError(f'Expected PermissionOverwrite received {perm.__class__.__name__}')

            allow, deny = perm.pair()
            overwrites_payload = {'allow': allow.value, 'deny': deny.value, 'id': target.id, 'type': abc._Overwrites.ROLE}

            if not isinstance(target, NewRole):
                raise TypeError(f'Expected NewRole received {perm.__class__.__name__}')

            perms.append(overwrites_payload)

        if perms:
            payload['permission_overwrites'] = perms

        if self.category:
            payload['parent_id'] = self.category.id

        return payload


class NewTextChannel(NewGuildChannel):
    def __init__(
        self,
        *,
        topic: Optional[str],
        slowmode_delay: Optional[int],
        nsfw: Optional[bool],
        default_auto_archive_duration: Optional[int],
        default_thread_slowmode_delay: Optional[int],
        **kwargs,
    ) -> None:
        super().__init__(**kwargs, type=ChannelType.text)
        self.topic = topic
        self.slowmode_delay = slowmode_delay
        self.nsfw = nsfw
        self.default_auto_archive_duration = default_auto_archive_duration
        self.default_thread_slowmode_delay = default_thread_slowmode_delay

    def _to_payload(self):
        payload: Dict[str, Any] = super()._to_payload()

        if self.topic is not None:
            payload['topic'] = self.topic

        if self.slowmode_delay is not None:
            payload['rate_limit_per_user'] = self.slowmode_delay

        if self.nsfw is not None:
            payload['nsfw'] = self.nsfw

        if self.default_auto_archive_duration is not None:
            payload['default_auto_archive_duration'] = self.default_auto_archive_duration

        if self.default_thread_slowmode_delay is not None:
            payload['default_thread_rate_limit_per_user'] = self.default_thread_slowmode_delay

        return payload


class NewVoiceChannel(NewGuildChannel):
    def __init__(
        self,
        *,
        bitrate: Optional[int] = None,
        user_limit: Optional[int] = None,
        rtc_region: Optional[Optional[str]] = None,
        video_quality_mode: Optional[VideoQualityMode] = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs, type=ChannelType.voice)

        self.bitrate = bitrate
        self.user_limit = user_limit
        self.rtc_region = rtc_region
        self.video_quality_mode = video_quality_mode

    def _to_payload(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = super()._to_payload()

        if self.bitrate is not None:
            payload['bitrate'] = self.bitrate

        if self.user_limit is not None:
            payload['user_limit'] = self.user_limit

        if self.rtc_region is not None:
            payload['rtc_region'] = self.rtc_region

        if self.video_quality_mode is not None:
            if not isinstance(self.video_quality_mode, VideoQualityMode):
                raise TypeError('video_quality_mode must be of type VideoQualityMode')
            payload['video_quality_mode'] = self.video_quality_mode.value

        return payload


class NewStageChannel(NewGuildChannel):
    def __init__(
        self,
        *,
        bitrate: Optional[int] = None,
        user_limit: Optional[int] = None,
        rtc_region: Optional[Optional[str]] = None,
        video_quality_mode: Optional[VideoQualityMode] = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs, type=ChannelType.stage_voice)

        self.bitrate = bitrate
        self.user_limit = user_limit
        self.rtc_region = rtc_region
        self.video_quality_mode = video_quality_mode

    def _to_payload(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = super()._to_payload()

        if self.bitrate is not None:
            payload['bitrate'] = self.bitrate

        if self.user_limit is not None:
            payload['user_limit'] = self.user_limit

        if self.rtc_region is not None:
            payload['rtc_region'] = self.rtc_region

        if self.video_quality_mode is not None:
            if not isinstance(self.video_quality_mode, VideoQualityMode):
                raise TypeError('video_quality_mode must be of type VideoQualityMode')
            payload['video_quality_mode'] = self.video_quality_mode.value

        return payload


class NewCategory(NewGuildChannel):
    def __init__(
        self,
        *,
        name: str,
        overwrites: Optional[Dict[NewRole, PermissionOverwrite]],
        guild: NewGuild,
    ) -> None:
        super().__init__(
            name=name,
            type=ChannelType.category,
            category=None,
            overwrites=overwrites,
            guild=guild,
        )

    def add_text_channel(self, name, **options) -> NewTextChannel:
        return self.guild.add_text_channel(name, **options, category=self)

    def add_voice_channel(self, name, **options) -> NewVoiceChannel:
        return self.guild.add_voice_channel(name, **options, category=self)

    def add_stage_channel(self, name, **options) -> NewStageChannel:
        return self.guild.add_stage_channel(name, **options, category=self)

    def add_forum(self, name, **options) -> NewForum:
        return self.guild.add_forum(name, **options, category=self)


class NewForum(NewGuildChannel):
    def __init__(
        self,
        *,
        topic: Optional[str],
        slowmode_delay: Optional[int],
        nsfw: Optional[bool],
        default_auto_archive_duration: Optional[int],
        default_thread_slowmode_delay: Optional[int],
        default_sort_order: Optional[ForumOrderType] = None,
        default_reaction_emoji: Optional[EmojiInputType] = None,
        default_layout: Optional[ForumLayoutType] = None,
        available_tags: Optional[Sequence[ForumTag]] = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs, type=ChannelType.text)
        self.topic = topic
        self.slowmode_delay = slowmode_delay
        self.nsfw = nsfw
        self.default_auto_archive_duration = default_auto_archive_duration
        self.default_thread_slowmode_delay = default_thread_slowmode_delay
        self.default_sort_order = default_sort_order
        self.default_reaction_emoji = default_reaction_emoji
        self.default_layout = default_layout
        self.available_tags = available_tags

    def _to_payload(self):
        payload: Dict[str, Any] = super()._to_payload()

        if self.topic is not None:
            payload['topic'] = self.topic

        if self.slowmode_delay is not None:
            payload['rate_limit_per_user'] = self.slowmode_delay

        if self.nsfw is not None:
            payload['nsfw'] = self.nsfw

        if self.default_auto_archive_duration is not None:
            payload['default_auto_archive_duration'] = self.default_auto_archive_duration

        if self.default_thread_slowmode_delay is not None:
            payload['default_thread_rate_limit_per_user'] = self.default_thread_slowmode_delay

        if self.default_sort_order is not None:
            if not isinstance(self.default_sort_order, ForumOrderType):
                raise TypeError(
                    f'default_sort_order parameter must be a ForumOrderType not {self.default_sort_order.__class__.__name__}'
                )

            payload['default_sort_order'] = self.default_sort_order.value

        if self.default_reaction_emoji is not None:
            if isinstance(self.default_reaction_emoji, _EmojiTag):
                payload['default_reaction_emoji'] = self.default_reaction_emoji._to_partial()._to_forum_tag_payload()
            elif isinstance(self.default_reaction_emoji, str):
                payload['default_reaction_emoji'] = PartialEmoji.from_str(
                    self.default_reaction_emoji
                )._to_forum_tag_payload()
            else:
                raise ValueError(f'default_reaction_emoji parameter must be either Emoji, PartialEmoji, or str')

        if self.default_layout is not None:
            if not isinstance(self.default_layout, ForumLayoutType):
                raise TypeError(
                    f'default_layout parameter must be a ForumLayoutType not {self.default_layout.__class__.__name__}'
                )

            payload['default_forum_layout'] = self.default_layout.value

        if self.available_tags is not None:
            payload['available_tags'] = [t.to_dict() for t in self.available_tags]

        return payload


class NewGuild:
    def __init__(
        self,
        *,
        name: str,
        icon: Optional[bytes] = None,
        afk_timeout: Optional[int] = None,
        verification_level: Optional[VerificationLevel] = None,
        notification_level: Optional[NotificationLevel] = None,
        content_filter: Optional[ContentFilter] = None,
        system_channel_flags: Optional[SystemChannelFlags] = None,
        state: ConnectionState,
    ) -> None:
        self.name = name
        self.icon = icon
        self.afk_timeout = afk_timeout
        self.verification_level = verification_level
        self.notification_level = notification_level
        self.content_filter = content_filter
        self.system_channel_flags = system_channel_flags

        self.roles: List[NewRole] = []
        self.channels: List[NewGuildChannel] = []

        self.afk_channel_id: Optional[int] = None
        self.system_channel_id: Optional[int] = None

        self._state = state

    @property
    def default_role(self):
        if not self.roles:
            self.add_role(name='@everyone')
        return self.roles[0]

    def add_role(
        self,
        *,
        name: str,
        permissions: Optional[Permissions] = None,
        color: Optional[Union[Colour, int]] = None,
        colour: Optional[Union[Colour, int]] = None,
        hoist: Optional[bool] = None,
        mentionable: Optional[bool] = None,
    ) -> NewRole:
        if not self.roles and name != '@everyone':
            self.default_role  # Populate @everyone role first.

        role = NewRole(
            name=name,
            permissions=permissions,
            colour=color or colour,
            hoist=hoist,
            mentionable=mentionable,
        )
        self.roles.append(role)
        return role

    def add_text_channel(
        self,
        name: str,
        *,
        category: Optional[NewCategory] = None,
        topic: Optional[str] = None,
        slowmode_delay: Optional[int] = None,
        nsfw: Optional[bool] = None,
        overwrites: Optional[Dict[NewRole, PermissionOverwrite]] = None,  # Only roles, since there won't be any members.
        default_auto_archive_duration: Optional[int] = None,
        default_thread_slowmode_delay: Optional[int] = None,
        is_system_channel: bool = False,
    ) -> NewTextChannel:
        channel = NewTextChannel(
            name=name,
            category=category,
            topic=topic,
            slowmode_delay=slowmode_delay,
            nsfw=nsfw,
            overwrites=overwrites,
            default_auto_archive_duration=default_auto_archive_duration,
            default_thread_slowmode_delay=default_thread_slowmode_delay,
            guild=self,
        )
        self.channels.append(channel)
        if is_system_channel:
            self.system_channel_id = channel.id
        return channel

    def add_voice_channel(
        self,
        name: str,
        *,
        category: Optional[NewCategory] = None,
        bitrate: Optional[int] = None,
        user_limit: Optional[int] = None,
        rtc_region: Optional[Optional[str]] = None,
        video_quality_mode: Optional[VideoQualityMode] = None,
        overwrites: Optional[Dict[NewRole, PermissionOverwrite]] = None,
        is_afk_channel: bool = False,
    ) -> NewVoiceChannel:
        channel = NewVoiceChannel(
            name=name,
            category=category,
            bitrate=bitrate,
            user_limit=user_limit,
            rtc_region=rtc_region,
            video_quality_mode=video_quality_mode,
            overwrites=overwrites,
            guild=self,
        )
        self.channels.append(channel)
        if is_afk_channel:
            self.afk_channel_id = channel.id
        return channel

    def add_stage_channel(
        self,
        name: str,
        *,
        category: Optional[NewCategory] = None,
        bitrate: Optional[int] = None,
        user_limit: Optional[int] = None,
        rtc_region: Optional[Optional[str]] = None,
        video_quality_mode: Optional[VideoQualityMode] = None,
        overwrites: Optional[Dict[NewRole, PermissionOverwrite]] = None,
    ) -> NewStageChannel:
        channel = NewStageChannel(
            name=name,
            category=category,
            bitrate=bitrate,
            user_limit=user_limit,
            rtc_region=rtc_region,
            video_quality_mode=video_quality_mode,
            overwrites=overwrites,
            guild=self,
        )
        self.channels.append(channel)
        return channel

    def add_category(
        self,
        name: str,
        *,
        overwrites: Optional[Dict[NewRole, PermissionOverwrite]] = None,
    ) -> NewCategory:
        channel = NewCategory(name=name, overwrites=overwrites, guild=self)
        self.channels.append(channel)
        return channel

    add_category_channel = add_category

    def add_forum(
        self,
        name: str,
        *,
        topic: Optional[str] = None,
        category: Optional[NewCategory] = None,
        slowmode_delay: Optional[int] = None,
        nsfw: Optional[bool] = None,
        overwrites: Optional[Dict[Union[NewRole, NewGuildChannel], PermissionOverwrite]] = None,
        default_auto_archive_duration: Optional[int] = None,
        default_thread_slowmode_delay: Optional[int] = None,
        default_sort_order: Optional[ForumOrderType] = None,
        default_reaction_emoji: Optional[EmojiInputType] = None,
        default_layout: Optional[ForumLayoutType] = None,
        available_tags: Optional[Sequence[ForumTag]] = None,
    ) -> NewForum:
        channel = NewForum(
            name=name,
            category=category,
            topic=topic,
            slowmode_delay=slowmode_delay,
            nsfw=nsfw,
            overwrites=overwrites,
            default_auto_archive_duration=default_auto_archive_duration,
            default_thread_slowmode_delay=default_thread_slowmode_delay,
            default_sort_order=default_sort_order,
            default_reaction_emoji=default_reaction_emoji,
            default_layout=default_layout,
            available_tags=available_tags,
            guild=self,
        )
        self.channels.append(channel)
        return channel

    def _to_payload(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {'name': self.name}

        if self.icon:
            payload['icon'] = _bytes_to_base64_data(self.icon)

        if self.afk_timeout is not None:
            payload['afk_timeout'] = self.afk_timeout

        if self.verification_level:
            payload['verification_level'] = self.verification_level.value

        if self.notification_level:
            payload['default_message_notifications'] = self.notification_level.value

        if self.content_filter:
            payload['explicit_content_filter'] = self.content_filter.value

        if self.system_channel_flags:
            payload['system_channel_flags'] = self.system_channel_flags.value

        if self.roles:
            payload['roles'] = [role._to_payload() for role in self.roles]

        if self.channels:
            payload['channels'] = [channel._to_payload() for channel in self.channels]

            if self.afk_channel_id:
                payload['afk_channel_id'] = self.afk_channel_id

            if self.system_channel_id:
                payload['system_channel_id'] = self.system_channel_id

        return payload

    async def _create_guild(self):
        payload = self._to_payload()
        data = await self._state.http.create_guild(**payload)
        return Guild(data=data, state=self._state)

    def __await__(self):
        return self._create_guild().__await__()


class NewTemplatedGuild:
    def __init__(
        self,
        *,
        name: str,
        code: str,
        icon: Optional[bytes] = None,
        state: ConnectionState,
    ):
        self.name = name
        self.icon = icon
        self.code = code
        self._state = state

    async def _create_guild(self):
        if self.icon is not None:
            icon_b64 = _bytes_to_base64_data(self.icon)
        else:
            icon_b64 = None

        data = await self._state.http.create_from_template(self.code, self.name, icon_b64)
        return Guild(data=data, state=self._state)

    def __await__(self):
        return self._create_guild().__await__()
