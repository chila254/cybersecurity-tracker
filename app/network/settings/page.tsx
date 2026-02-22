'use client';

import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { AlertCircle, Settings, Check, Loader } from 'lucide-react';

interface WiFiConfig {
  router_type: string;
  router_url: string;
  router_username: string;
  dns_log_source: string;
  is_enabled: boolean;
}

interface NetworkPolicy {
  id: string;
  name: string;
  description: string;
  block_categories: string[];
  is_active: boolean;
}

const DOMAIN_CATEGORIES = [
  { value: 'social', label: '🔵 Social Media' },
  { value: 'streaming', label: '🎬 Video Streaming' },
  { value: 'adult', label: '⛔ Adult Content' },
  { value: 'gambling', label: '🎰 Gambling' },
  { value: 'malware', label: '🚨 Malware/Phishing' }
];

export default function NetworkSettingsPage() {
  const [config, setConfig] = useState<WiFiConfig | null>(null);
  const [policies, setPolicies] = useState<NetworkPolicy[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [step, setStep] = useState<'detect' | 'configure' | 'done'>('detect');

  const [detecting, setDetecting] = useState(false);
  const [detectionResult, setDetectionResult] = useState<any>(null);

  const [password, setPassword] = useState('');
  const [testingConnection, setTestingConnection] = useState(false);

  const [policyForm, setPolicyForm] = useState({
    name: '',
    description: '',
    block_categories: [] as string[]
  });

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';
  const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    try {
      setLoading(true);
      const res = await fetch(`${apiUrl}/network/wifi-config`, {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (res.ok) {
        setConfig(await res.json());
        setStep('done');
      } else {
        setStep('detect');
      }

      const policiesRes = await fetch(`${apiUrl}/network/policies`, {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (policiesRes.ok) {
        setPolicies(await policiesRes.json());
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load settings');
    } finally {
      setLoading(false);
    }
  };

  const handleDetectRouter = async () => {
    try {
      setDetecting(true);
      setDetectionResult(null);
      
      const res = await fetch(`${apiUrl}/network/wifi-config/detect`, {
        method: 'POST'
      });

      const result = await res.json();
      setDetectionResult(result);

      if (result.detected) {
        setStep('configure');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Detection failed');
    } finally {
      setDetecting(false);
    }
  };

  const handleTestConnection = async () => {
    if (!password) {
      alert('Please enter your router password');
      return;
    }

    try {
      setTestingConnection(true);

      const res = await fetch(`${apiUrl}/network/wifi-config/test-connection`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          router_url: detectionResult.router_url,
          password: password,
          router_type: detectionResult.router_type
        })
      });

      const result = await res.json();

      if (result.success) {
        // Save configuration
        const saveRes = await fetch(`${apiUrl}/network/wifi-config`, {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            router_type: detectionResult.router_type,
            router_url: detectionResult.router_url,
            router_username: 'admin',
            router_password: password
          })
        });

        if (saveRes.ok) {
          setConfig(await saveRes.json());
          setStep('done');
          alert('✅ Router configured successfully!');
        }
      } else {
        alert('❌ Connection failed: ' + (result.message || result.error));
      }
    } catch (err) {
      alert('Error: ' + (err instanceof Error ? err.message : 'Unknown error'));
    } finally {
      setTestingConnection(false);
    }
  };

  const handleCreatePolicy = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      const res = await fetch(`${apiUrl}/network/policies`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(policyForm)
      });

      if (!res.ok) throw new Error('Failed to create policy');

      alert('✅ Policy created successfully');
      setPolicyForm({ name: '', description: '', block_categories: [] });
      fetchSettings();
    } catch (err) {
      alert('❌ Error: ' + (err instanceof Error ? err.message : 'Unknown error'));
    }
  };

  if (loading) return <div className="p-8 text-center">Loading settings...</div>;

  return (
    <div className="space-y-8 p-8">
      {/* Header */}
      <div>
        <h1 className="flex items-center gap-2 text-3xl font-bold">
          <Settings className="h-8 w-8" />
          Network Settings
        </h1>
        <p className="text-gray-600">Auto-detect and configure your WiFi router</p>
      </div>

      {error && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="flex items-center gap-3 pt-6">
            <AlertCircle className="h-5 w-5 text-red-600" />
            <p className="text-red-800">{error}</p>
          </CardContent>
        </Card>
      )}

      {/* Step 1: Auto-Detect */}
      {step === 'detect' && !config && (
        <Card>
          <CardHeader>
            <CardTitle>🔍 Auto-Detect Router</CardTitle>
            <CardDescription>Let us find your WiFi router automatically</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {detectionResult ? (
              detectionResult.detected ? (
                <div className="space-y-3 rounded bg-green-50 p-4">
                  <div className="flex items-center gap-2 text-green-800">
                    <Check className="h-5 w-5" />
                    <span className="font-semibold">Router Detected!</span>
                  </div>
                  <p className="text-sm">
                    <span className="font-semibold">Type:</span> {detectionResult.router_type.toUpperCase()}
                  </p>
                  <p className="text-sm">
                    <span className="font-semibold">URL:</span> {detectionResult.router_url}
                  </p>
                  <p className="text-xs text-green-700">{detectionResult.message}</p>
                  <Button onClick={() => setStep('configure')}>Continue to Login</Button>
                </div>
              ) : (
                <div className="space-y-3 rounded bg-yellow-50 p-4">
                  <p className="text-sm text-yellow-800">{detectionResult.message}</p>
                  {detectionResult.suggestions && (
                    <ul className="list-inside list-disc space-y-1 text-xs text-yellow-700">
                      {detectionResult.suggestions.map((s: string, i: number) => (
                        <li key={i}>{s}</li>
                      ))}
                    </ul>
                  )}
                  <Button variant="outline" size="sm" onClick={handleDetectRouter}>
                    Try Again
                  </Button>
                </div>
              )
            ) : (
              <Button
                onClick={handleDetectRouter}
                disabled={detecting}
                className="w-full"
                size="lg"
              >
                {detecting ? (
                  <>
                    <Loader className="mr-2 h-4 w-4 animate-spin" />
                    Scanning Network...
                  </>
                ) : (
                  '🔍 Detect My Router'
                )}
              </Button>
            )}
          </CardContent>
        </Card>
      )}

      {/* Step 2: Configure (Enter Password) */}
      {step === 'configure' && detectionResult?.detected && (
        <Card>
          <CardHeader>
            <CardTitle>🔐 Router Login</CardTitle>
            <CardDescription>
              Detected: {detectionResult.router_type.toUpperCase()} at {detectionResult.router_url}
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="block text-sm font-medium">Router Admin Password</label>
              <input
                type="password"
                placeholder="Enter your router admin password"
                value={password}
                onChange={e => setPassword(e.target.value)}
                className="mt-1 block w-full rounded border px-3 py-2"
                onKeyPress={e => e.key === 'Enter' && handleTestConnection()}
              />
              <p className="mt-1 text-xs text-gray-500">
                Usually 'admin' or found on the router label
              </p>
            </div>

            <div className="flex gap-2">
              <Button
                onClick={handleTestConnection}
                disabled={testingConnection || !password}
                className="flex-1"
              >
                {testingConnection ? (
                  <>
                    <Loader className="mr-2 h-4 w-4 animate-spin" />
                    Testing...
                  </>
                ) : (
                  '🔗 Connect & Save'
                )}
              </Button>
              <Button
                variant="outline"
                onClick={() => setStep('detect')}
              >
                Back
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Step 3: Done / Configured */}
      {step === 'done' && config && (
        <Card className="border-green-200 bg-green-50">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-green-800">
              <Check className="h-5 w-5" />
              ✅ Router Connected
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-sm">
            <p>
              <span className="font-semibold">Router Type:</span> {config.router_type.toUpperCase()}
            </p>
            <p>
              <span className="font-semibold">URL:</span> {config.router_url}
            </p>
            {config.is_enabled && <p className="text-green-800">✅ Enabled and ready to sync</p>}
            <Button
              variant="outline"
              onClick={() => {
                setPassword('');
                setDetectionResult(null);
                setStep('detect');
              }}
              size="sm"
            >
              Change Router
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Network Policies */}
      <Card>
        <CardHeader>
          <CardTitle>🚫 Network Policies</CardTitle>
          <CardDescription>Block categories of websites</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Policy List */}
          {policies.length > 0 && (
            <div className="space-y-2">
              {policies.map(policy => (
                <div
                  key={policy.id}
                  className={`rounded border p-3 ${
                    policy.is_active ? 'border-blue-200 bg-blue-50' : 'border-gray-200'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-semibold">{policy.name}</p>
                      <p className="text-sm text-gray-600">{policy.description}</p>
                      <div className="mt-2 flex flex-wrap gap-1">
                        {policy.block_categories.map(cat => (
                          <span key={cat} className="inline-block rounded bg-red-100 px-2 py-1 text-xs text-red-800">
                            ❌ {cat}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Create New Policy */}
          <form onSubmit={handleCreatePolicy} className="space-y-4 border-t pt-4">
            <h3 className="font-semibold">Create New Policy</h3>

            <div>
              <label className="block text-sm font-medium">Policy Name *</label>
              <input
                type="text"
                placeholder="e.g., Block Adult Content"
                value={policyForm.name}
                onChange={e => setPolicyForm({ ...policyForm, name: e.target.value })}
                className="mt-1 block w-full rounded border px-3 py-2"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium">Description</label>
              <input
                type="text"
                placeholder="Policy description"
                value={policyForm.description}
                onChange={e => setPolicyForm({ ...policyForm, description: e.target.value })}
                className="mt-1 block w-full rounded border px-3 py-2"
              />
            </div>

            <div>
              <label className="block text-sm font-medium">Block Categories</label>
              <div className="mt-2 space-y-2">
                {DOMAIN_CATEGORIES.map(cat => (
                  <label key={cat.value} className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={policyForm.block_categories.includes(cat.value)}
                      onChange={e => {
                        if (e.target.checked) {
                          setPolicyForm({
                            ...policyForm,
                            block_categories: [...policyForm.block_categories, cat.value]
                          });
                        } else {
                          setPolicyForm({
                            ...policyForm,
                            block_categories: policyForm.block_categories.filter(c => c !== cat.value)
                          });
                        }
                      }}
                    />
                    <span>{cat.label}</span>
                  </label>
                ))}
              </div>
            </div>

            <Button type="submit" disabled={!policyForm.name || policyForm.block_categories.length === 0}>
              Create Policy
            </Button>
          </form>
        </CardContent>
      </Card>

      {/* Tips */}
      <Card className="border-blue-200 bg-blue-50">
        <CardHeader>
          <CardTitle>💡 Tips</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 text-sm">
          <p>✅ Auto-detection works best on the same network as your router</p>
          <p>✅ Default admin password is usually 'admin' or on your router label</p>
          <p>✅ Once connected, click "Sync Now" to discover connected devices</p>
          <p>✅ Create policies to block unwanted content categories</p>
        </CardContent>
      </Card>
    </div>
  );
}
