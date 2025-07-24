from typing import Dict
import re
import yaml

# 입력된 Puppet 스타일 변수 선언
puppet_vars = """
Optional[Enum['on', 'off']] $absolute_redirect             = undef,
Enum['on', 'off'] $accept_mutex                            = 'on',
Nginx::Time $accept_mutex_delay                            = '500ms',
Nginx::Size $client_body_buffer_size                       = '128k',
Nginx::Size $client_max_body_size                          = '10m',
Nginx::Time $client_body_timeout                           = '60s',
Nginx::Time $send_timeout                                  = '60s',
Nginx::Time $lingering_timeout                             = '5s',
Optional[Enum['on','off','always']] $lingering_close       = undef,
Optional[String[1]] $lingering_time                        = undef,
Optional[Enum['on', 'off']] $etag                          = undef,
Optional[String] $events_use                               = undef,
Array[Nginx::DebugConnection] $debug_connections           = [],
Nginx::Time $fastcgi_cache_inactive                        = '20m',
Optional[String] $fastcgi_cache_key                        = undef,
String $fastcgi_cache_keys_zone                            = 'd3:100m',
String $fastcgi_cache_levels                               = '1',
Nginx::Size $fastcgi_cache_max_size                        = '500m',
Optional[String] $fastcgi_cache_path                       = undef,
Optional[String] $fastcgi_cache_use_stale                  = undef,
Enum['on', 'off'] $gzip                                    = 'off',
Optional[String] $gzip_buffers                             = undef,
Integer $gzip_comp_level                                   = 1,
String $gzip_disable                                       = 'msie6',
Integer $gzip_min_length                                   = 20,
Enum['1.0','1.1'] $gzip_http_version                       = '1.1',
Variant[Nginx::GzipProxied, Array[Nginx::GzipProxied]] $gzip_proxied = 'off',
Optional[Variant[String[1],Array[String[1]]]] $gzip_types  = undef,
Enum['on', 'off'] $gzip_vary                               = 'off',
Optional[Enum['on', 'off', 'always']] $gzip_static         = undef,
Optional[Variant[Hash, Array]] $http_cfg_prepend           = undef,
Optional[Variant[Hash, Array]] $http_cfg_append            = undef,
Optional[Variant[Array[String], String]] $http_raw_prepend = undef,
Optional[Variant[Array[String], String]] $http_raw_append  = undef,
Enum['on', 'off'] $http_tcp_nodelay                        = 'on',
Enum['on', 'off'] $http_tcp_nopush                         = 'off',
Nginx::Time $keepalive_timeout                             = '65s',
Integer $keepalive_requests                                = 100,
Hash[String[1], Nginx::LogFormat] $log_format              = {},
Hash[String[1], Nginx::LogFormat] $stream_log_format       = {},
Boolean $mail                                              = false,
Optional[Integer] $map_hash_bucket_size                    = undef,
Optional[Integer] $map_hash_max_size                       = undef,
Variant[String, Boolean] $mime_types_path                  = 'mime.types',
Boolean $stream                                            = false,
String $multi_accept                                       = 'off',
Integer $names_hash_bucket_size                            = 64,
Integer $names_hash_max_size                               = 512,
Variant[Boolean,Array,Hash] $nginx_cfg_prepend             = false,
String $proxy_buffers                                      = '32 4k',
Nginx::Size $proxy_buffer_size                             = '8k',
Nginx::Time $proxy_cache_inactive                          = '20m',
String $proxy_cache_keys_zone                              = 'd2:100m',
String $proxy_cache_levels                                 = '1',
Nginx::Size $proxy_cache_max_size                          = '500m',
Optional[Variant[Hash, String]] $proxy_cache_path          = undef,
Optional[Integer] $proxy_cache_loader_files                = undef,
Optional[String] $proxy_cache_loader_sleep                 = undef,
Optional[String] $proxy_cache_loader_threshold             = undef,
Optional[Enum['on', 'off']] $proxy_use_temp_path           = undef,
Nginx::Time $proxy_connect_timeout                         = '90s',
Integer $proxy_headers_hash_bucket_size                    = 64,
Optional[String] $proxy_http_version                       = undef,
Nginx::Time $proxy_read_timeout                            = '90s',
Optional[String] $proxy_redirect                           = undef,
Nginx::Time $proxy_send_timeout                            = '90s',
Array $proxy_set_header                                    = [
   'Host $host',
   'X-Real-IP $remote_addr',
   'X-Forwarded-For $proxy_add_x_forwarded_for',
   'X-Forwarded-Host $host',
   'X-Forwarded-Proto $scheme',
   'Proxy ""',
 ],
 Array $proxy_hide_header                                   = [],
 Array $proxy_pass_header                                   = [],
 Array $proxy_ignore_header                                 = [],
 Optional[Nginx::Size] $proxy_max_temp_file_size            = undef,
 Optional[Nginx::Size] $proxy_busy_buffers_size             = undef,
 Enum['on', 'off'] $sendfile                                = 'on',
 Enum['on', 'off'] $server_tokens                           = 'on',
 Enum['on', 'off'] $spdy                                    = 'off',
 Enum['on', 'off'] $http2                                   = 'off',
 Enum['on', 'off'] $ssl_stapling                            = 'off',
 Enum['on', 'off'] $ssl_stapling_verify                     = 'off',
 Stdlib::Absolutepath $snippets_dir                         = $nginx::params::snippets_dir,
 Boolean $manage_snippets_dir                               = true,
 Variant[Integer,String] $types_hash_bucket_size            = '512',
 Variant[Integer,String] $types_hash_max_size               = '1024',
 Integer $worker_connections                                = 1024,
 Enum['on', 'off'] $ssl_prefer_server_ciphers               = 'on',
 Variant[Integer, Enum['auto']] $worker_processes           = 'auto',
 Integer $worker_rlimit_nofile                              = 1024,
 Optional[Enum['on', 'off']] $pcre_jit                      = undef,
 String $ssl_protocols                                      = 'TLSv1 TLSv1.1 TLSv1.2',
 String $ssl_ciphers                                        = 'ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-AES128-SHA256:ECDHE-RSA-AES128-SHA256:ECDHE-ECDSA-AES128-SHA:ECDHE-RSA-AES256-SHA384:ECDHE-RSA-AES128-SHA:ECDHE-ECDSA-AES256-SHA384:ECDHE-ECDSA-AES256-SHA:ECDHE-RSA-AES256-SHA:DHE-RSA-AES128-SHA256:DHE-RSA-AES128-SHA:DHE-RSA-AES256-SHA256:DHE-RSA-AES256-SHA:ECDHE-ECDSA-DES-CBC3-SHA:ECDHE-RSA-DES-CBC3-SHA:EDH-RSA-DES-CBC3-SHA:AES128-GCM-SHA256:AES256-GCM-SHA384:AES128-SHA256:AES256-SHA256:AES128-SHA:AES256-SHA:DES-CBC3-SHA:!DSS', # lint:ignore:140chars
  Optional[Stdlib::Unixpath] $ssl_dhparam                    = undef,
  Optional[String] $ssl_ecdh_curve                           = undef,
  String $ssl_session_cache                                  = 'shared:SSL:10m',
  Nginx::Time $ssl_session_timeout                           = '5m',
  Optional[Enum['on', 'off']] $ssl_session_tickets           = undef,
  Optional[Stdlib::Absolutepath] $ssl_session_ticket_key     = undef,
  Optional[String] $ssl_buffer_size                          = undef,
  Optional[Stdlib::Absolutepath] $ssl_crl                    = undef,
  Optional[Stdlib::Absolutepath] $ssl_stapling_file          = undef,
  Optional[String] $ssl_stapling_responder                   = undef,
  Optional[Stdlib::Absolutepath] $ssl_trusted_certificate    = undef,
  Optional[Integer] $ssl_verify_depth                        = undef,
  Optional[Stdlib::Absolutepath] $ssl_password_file          = undef,
  Optional[Enum['on', 'off']] $reset_timedout_connection     = undef,
"""

# 정규식으로 변수명과 기본값 추출
pattern = re.compile(r'\$\s*(\w+)\s*=\s*(.+?),?$')

# 결과 저장용 딕셔너리
yaml_dict: Dict[str, object] = {}

for line in puppet_vars.strip().splitlines():
    match = pattern.search(line)
    if match:
        key = match.group(1).strip()
        value = match.group(2).strip().strip("'\"")  # 양쪽 따옴표 제거
        full_key = f'nginx::config::{key}'
        yaml_dict[full_key] = None if value.lower() == 'undef' else value

# YAML 출력
print(yaml.dump(yaml_dict, default_flow_style=False, sort_keys=False))

# # 파일로 저장 (선택)
# with open('nginx_config.yaml', 'w') as f:
#     yaml.dump(yaml_dict, f, default_flow_style=False, sort_keys=False)
