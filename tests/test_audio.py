from pathlib import Path
import logging

import pytest

from voicebrief import audio


def test_calculate_segment_duration_uses_size_and_duration():
    max_chunk_size_bytes = 20 * 1024 * 1024
    file_size_bytes = 28 * 1024 * 1024
    duration_seconds = 20 * 60

    segment_seconds = audio._calculate_segment_duration_seconds(
        file_size_bytes,
        duration_seconds,
        max_chunk_size_bytes,
    )

    assert segment_seconds == 728


def test_calculate_segment_duration_validates_inputs():
    with pytest.raises(ValueError):
        audio._calculate_segment_duration_seconds(0, 60.0, 1024)

    with pytest.raises(ValueError):
        audio._calculate_segment_duration_seconds(1024, 0, 1024)


def test_resplit_oversized_chunks_only_reprocesses_large_files(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    small = tmp_path / "small.mp3"
    large = tmp_path / "large.mp3"
    part_a = tmp_path / "large_part_a.mp3"
    part_b = tmp_path / "large_part_b.mp3"

    small.write_bytes(b"a" * 10)
    large.write_bytes(b"b" * 30)
    part_a.write_bytes(b"c" * 15)
    part_b.write_bytes(b"d" * 12)

    calls: list[Path] = []

    def fake_partition(path: Path, max_chunk_size_bytes: int):
        calls.append(path)
        assert max_chunk_size_bytes == 20
        return [part_a, part_b]

    monkeypatch.setattr(audio, "_partition_sound_file", fake_partition)

    result = audio._resplit_oversized_chunks(
        [small, large],
        20,
        logging.getLogger("test.voicebrief.audio"),
    )

    assert result == [small, part_a, part_b]
    assert calls == [large]
