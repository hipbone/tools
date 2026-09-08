#!/usr/bin/env python3
"""
GitLab 그룹의 모든 프로젝트에서 커밋 수를 가져오는 스크립트

사용법:
    python get_group_projects_commits.py <GROUP_ID> [--url GITLAB_URL] [--token TOKEN]

환경변수:
    GITLAB_URL - GitLab 인스턴스 URL (기본값: https://gitlab.com)
    GITLAB_TOKEN - GitLab Private Token
"""

import os
import sys
import argparse
import requests
import csv
from typing import List, Dict, Optional
from datetime import datetime


class GitLabClient:
    def __init__(self, url: str, token: str):
        self.url = url.rstrip("/")
        self.token = token
        self.headers = {"PRIVATE-TOKEN": token}

    def get_all_group_projects(
        self, group_id: str, include_subgroups: bool = True
    ) -> List[Dict]:
        """그룹의 모든 프로젝트 가져오기 (페이지네이션 처리)"""
        projects = []
        page = 1
        per_page = 100

        while True:
            url = f"{self.url}/api/v4/groups/{group_id}/projects"
            params = {
                "include_subgroups": str(include_subgroups).lower(),
                "per_page": per_page,
                "page": page,
            }

            try:
                response = requests.get(url, headers=self.headers, params=params)
                response.raise_for_status()
                data = response.json()

                if not data:
                    break

                projects.extend(data)

                # 다음 페이지가 없으면 종료
                if len(data) < per_page:
                    break

                page += 1

            except requests.exceptions.RequestException as e:
                print(f"오류 발생: {e}", file=sys.stderr)
                if hasattr(e, "response") and e.response is not None:
                    print(f"응답: {e.response.text}", file=sys.stderr)
                sys.exit(1)

        return projects

    def get_commit_count(
        self,
        project_id: int,
        ref_name: str = None,
        since: Optional[str] = None,
        until: Optional[str] = None,
    ) -> tuple[int, Optional[str]]:
        """프로젝트의 커밋 수와 마지막 커밋 날짜 가져오기

        since/until이 주어지면 해당 기간(ISO 8601)의 커밋만 집계한다.
        """
        if not ref_name or ref_name == "null":
            return 0, None

        url = f"{self.url}/api/v4/projects/{project_id}/repository/commits"
        params = {"ref_name": ref_name, "per_page": 100}
        if since:
            params["since"] = since
        if until:
            params["until"] = until

        try:
            # 첫 페이지 요청하여 마지막 커밋 날짜와 전체 개수 확인
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()

            # 마지막 커밋 날짜
            data = response.json()
            last_commit_date = None
            if data and len(data) > 0:
                last_commit_date = data[0].get("committed_date", None)

            # 전체 커밋 수는 여러 헤더에서 시도
            total_count = 0

            # X-Total 헤더 확인
            if "X-Total" in response.headers:
                total_count = int(response.headers["X-Total"])
            # X-Total-Pages 헤더로 계산
            elif "X-Total-Pages" in response.headers:
                total_pages = int(response.headers["X-Total-Pages"])
                per_page = int(response.headers.get("X-Per-Page", 100))

                if total_pages == 1:
                    # 페이지가 1개면 현재 데이터 개수가 전체
                    total_count = len(data)
                else:
                    # 마지막 페이지를 요청하여 정확한 개수 계산
                    last_page_params = {**params, "per_page": per_page, "page": total_pages}
                    last_response = requests.get(url, headers=self.headers, params=last_page_params)
                    last_response.raise_for_status()
                    last_data = last_response.json()
                    total_count = (total_pages - 1) * per_page + len(last_data)
            else:
                # 헤더가 없으면 모든 페이지를 순회하여 카운트 (느림)
                total_count = len(data)
                page = 2
                while len(data) == params["per_page"]:
                    page_params = {**params, "per_page": 100, "page": page}
                    page_response = requests.get(url, headers=self.headers, params=page_params)
                    page_response.raise_for_status()
                    data = page_response.json()
                    total_count += len(data)
                    page += 1

                    # 너무 많은 커밋이 있으면 중단 (성능 보호)
                    if page > 100:  # 최대 10,000개 커밋까지만
                        total_count = f"{total_count}+"
                        break

            return total_count, last_commit_date

        except requests.exceptions.RequestException as e:
            print(f"프로젝트 {project_id} 커밋 조회 오류: {e}", file=sys.stderr)
            return 0, None


def main():
    parser = argparse.ArgumentParser(
        description="GitLab 그룹의 모든 프로젝트에서 커밋 수를 가져옵니다.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  %(prog)s 123
  %(prog)s my-group --url https://gitlab.example.com
  %(prog)s my-group --token glpat-xxxxxxxxxxxx
  %(prog)s my-group --url https://gitlab.example.com --token glpat-xxxxxxxxxxxx --output commits.csv
  %(prog)s my-group --since 2026-01-01 --until 2026-06-16
        """,
    )

    parser.add_argument("group_id", help="GitLab 그룹 ID 또는 경로")
    parser.add_argument(
        "--url",
        default=os.getenv("GITLAB_URL", "https://gitlab.com"),
        help="GitLab 인스턴스 URL (기본값: https://gitlab.com, 환경변수: GITLAB_URL)",
    )
    parser.add_argument(
        "--token",
        default=os.getenv("GITLAB_TOKEN"),
        help="GitLab Private Token (환경변수: GITLAB_TOKEN)",
    )
    parser.add_argument("--no-subgroups", action="store_true", help="하위 그룹 제외")
    parser.add_argument("--output", "-o", help="결과를 CSV 파일로 저장")
    parser.add_argument(
        "--since",
        help="이 날짜 이후의 커밋만 집계 (예: 2026-01-01, ISO 8601)",
    )
    parser.add_argument(
        "--until",
        help="이 날짜 이전의 커밋만 집계 (예: 2026-06-16, ISO 8601)",
    )

    args = parser.parse_args()

    # 기간 인자 정규화 (날짜만 입력 시 ISO 8601 형식으로 보정)
    def normalize_dt(value: Optional[str], end_of_day: bool) -> Optional[str]:
        if not value:
            return None
        # 날짜만(YYYY-MM-DD) 입력된 경우 시각을 보정
        if len(value) == 10 and value.count("-") == 2:
            return f"{value}T23:59:59Z" if end_of_day else f"{value}T00:00:00Z"
        return value

    since = normalize_dt(args.since, end_of_day=False)
    until = normalize_dt(args.until, end_of_day=True)

    # 토큰 확인
    if not args.token:
        print("오류: GitLab Private Token이 필요합니다.", file=sys.stderr)
        print(
            "--token 옵션 또는 GITLAB_TOKEN 환경변수로 토큰을 제공하세요.",
            file=sys.stderr,
        )
        sys.exit(1)

    # GitLab 클라이언트 생성
    client = GitLabClient(args.url, args.token)

    print("=" * 50)
    print("GitLab 그룹 프로젝트 커밋 수 조회")
    print("=" * 50)
    print(f"GitLab URL: {args.url}")
    print(f"그룹 ID: {args.group_id}")
    print(f"하위 그룹 포함: {not args.no_subgroups}")
    if since or until:
        print(f"기간: {since or '처음'} ~ {until or '현재'}")
    print()

    # 프로젝트 목록 가져오기
    print("프로젝트 목록을 가져오는 중...", file=sys.stderr)
    projects = client.get_all_group_projects(
        args.group_id, include_subgroups=not args.no_subgroups
    )
    print(f"총 {len(projects)}개의 프로젝트를 찾았습니다.", file=sys.stderr)
    print(file=sys.stderr)

    # 결과 저장
    results = []

    # 각 프로젝트의 커밋 수 조회
    for idx, project in enumerate(projects, 1):
        project_id = project["id"]
        project_name = project["name"]
        project_path = project["path_with_namespace"]
        default_branch = project.get("default_branch", "main")
        web_url = project["web_url"]

        print(f"[{idx}/{len(projects)}] {project_name} 처리 중...", file=sys.stderr)

        commit_count, last_commit_date = client.get_commit_count(
            project_id, default_branch, since=since, until=until
        )

        # 날짜 포맷팅
        if last_commit_date:
            try:
                dt = datetime.fromisoformat(last_commit_date.replace("Z", "+00:00"))
                last_commit_date = dt.strftime("%Y-%m-%d %H:%M:%S")
            except:
                pass
        else:
            last_commit_date = "N/A"

        results.append(
            {
                "project_id": project_id,
                "project_name": project_name,
                "namespace": project_path,
                "commit_count": commit_count,
                "default_branch": default_branch or "N/A",
                "last_commit_date": last_commit_date,
                "web_url": web_url,
            }
        )

    # 결과 출력
    print(file=sys.stderr)
    print("=" * 50)

    # CSV 형식으로 출력
    fieldnames = [
        "project_id",
        "project_name",
        "namespace",
        "commit_count",
        "default_branch",
        "last_commit_date",
        "web_url",
    ]

    if args.output:
        # 파일로 저장
        with open(args.output, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        print(f"결과가 {args.output}에 저장되었습니다.")
    else:
        # 표준 출력
        writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    # 요약 통계
    total_commits = sum(r["commit_count"] for r in results)
    print(file=sys.stderr)
    print("요약:", file=sys.stderr)
    print(f"  총 프로젝트 수: {len(results)}", file=sys.stderr)
    print(f"  총 커밋 수: {total_commits:,}", file=sys.stderr)
    print(
        (
            f"  평균 커밋 수: {total_commits / len(results):.1f}"
            if results
            else "  평균 커밋 수: 0"
        ),
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
