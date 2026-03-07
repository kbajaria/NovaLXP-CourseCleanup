<?php
namespace local_novalxpcoursefactory;

defined('MOODLE_INTERNAL') || die();

class client {
    /**
     * Emit a developer log line for course factory activity.
     *
     * @param string $message
     * @return void
     */
    private static function log(string $message): void {
        error_log('[NovaLXPCourseFactory] ' . $message);
    }

    /**
     * Invoke Lambda via AWS CLI using the instance role.
     *
     * @param string $functionname
     * @param string $region
     * @param array $payload
     * @param int $timeoutseconds
     * @return array
     */
    public static function invoke_async(string $functionname, string $region, array $payload): array {
        $requestid = isset($payload['request_id']) ? (string)$payload['request_id'] : 'unknown';
        $payloadfile = tempnam(sys_get_temp_dir(), 'novalxpcoursefactory_payload_');
        $outputfile = tempnam(sys_get_temp_dir(), 'novalxpcoursefactory_output_');

        if ($payloadfile === false || $outputfile === false) {
            self::log("request_id={$requestid} temp_file_creation_failed");
            return [
                'ok' => false,
                'status' => 0,
                'error' => get_string('invokeerror', 'local_novalxpcoursefactory'),
            ];
        }

        file_put_contents($payloadfile, json_encode($payload));
        self::log("request_id={$requestid} invoking_lambda_async function={$functionname} region={$region}");

        $command = [
            'aws',
            'lambda',
            'invoke',
            '--region',
            $region,
            '--function-name',
            $functionname,
            '--invocation-type',
            'Event',
            '--cli-binary-format',
            'raw-in-base64-out',
            '--cli-connect-timeout',
            '10',
            '--payload',
            'fileb://' . $payloadfile,
            $outputfile,
        ];

        $descriptor = [
            0 => ['pipe', 'r'],
            1 => ['pipe', 'w'],
            2 => ['pipe', 'w'],
        ];

        $process = proc_open($command, $descriptor, $pipes);
        if (!is_resource($process)) {
            @unlink($payloadfile);
            @unlink($outputfile);
            self::log("request_id={$requestid} lambda_process_open_failed");
            return [
                'ok' => false,
                'status' => 0,
                'error' => get_string('invokeerror', 'local_novalxpcoursefactory'),
            ];
        }

        fclose($pipes[0]);
        $stdout = stream_get_contents($pipes[1]);
        fclose($pipes[1]);
        $stderr = stream_get_contents($pipes[2]);
        fclose($pipes[2]);
        $statuscode = proc_close($process);

        $responsebody = is_file($outputfile) ? (string)file_get_contents($outputfile) : '';
        @unlink($payloadfile);
        @unlink($outputfile);

        $metadata = trim($stdout);
        $decoded = json_decode($metadata !== '' ? $metadata : $responsebody, true);
        if (!is_array($decoded)) {
            $decoded = [];
        }

        self::log(
            "request_id={$requestid} lambda_completed status={$statuscode}" .
            (!empty($decoded['StatusCode']) ? " invoke_status=" . (int)$decoded['StatusCode'] : '') .
            (!empty($decoded['FunctionError']) ? " function_error=" . (string)$decoded['FunctionError'] : '')
        );

        return [
            'ok' => $statuscode === 0 && (int)($decoded['StatusCode'] ?? 0) === 202,
            'status' => $statuscode,
            'body' => $decoded,
            'raw' => $metadata !== '' ? $metadata : $responsebody,
            'error' => trim($stderr . "\n" . $stdout),
        ];
    }
}
